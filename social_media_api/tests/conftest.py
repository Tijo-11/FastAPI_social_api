import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient, Request, Response

from social_media_api.tests.helpers import create_post  # noqa

os.environ["ENV_STATE"] = "testing"


from social_media_api.database import database, user_table  # noqa: E402
from social_media_api.main import app  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield database
    await database.disconnect()


@pytest.fixture()
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture()
async def registered_user(async_client: AsyncClient) -> dict:
    user_details = {"email": "test@example.net", "password": "1234"}
    await async_client.post("/register", json=user_details)
    query = user_table.select().where(user_table.c.email == user_details["email"])
    user = await database.fetch_one(query)
    user_details["id"] = user.id
    return user_details


@pytest.fixture()
async def logged_in_token(async_client: AsyncClient, confirmed_user: dict) -> str:
    response = await async_client.post("/token", json=confirmed_user)
    # registered usre includes user_id, but pydantic will strip it
    return response.json()["access_token"]


# fixture to use confirme users
@pytest.fixture()
async def confirmed_user(registered_user: dict) -> dict:
    query = (
        user_table.update()
        .where(user_table.c.email == registered_user["email"])
        .values(confirmed=True)
    )
    await database.execute(query)
    return registered_user


# mailgun email sending
@pytest.fixture(autouse=True)
async def mock_httpx_client(mocker):
    mocked_client = mocker.patch("social_media_api.tasks.httpx.AsyncClient")

    mocked_async_client = Mock()
    response = Response(status_code=200, content="", request=Request("POST", "//"))
    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client

    return mocked_async_client


##fixtures forpost test
@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post("Test Post", async_client, logged_in_token)

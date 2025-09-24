import pytest
from httpx import AsyncClient


async def register_user(async_client: AsyncClient, email: str, password: str):
    return await async_client.post(
        "/register", json={"email": email, "password": password}
    )


@pytest.mark.anyio
async def test_register_user(async_client: AsyncClient):
    response = await register_user(async_client, "test@example.net", "1234")

    assert response.status_code == 201
    assert "User created" in response.json()["detail"]


@pytest.mark.anyio
async def test_register_existing_user(async_client: AsyncClient, registered_user):
    response = await register_user(
        async_client, registered_user["email"], "newpassword"
    )

    assert response.status_code == 400
    assert "already" in response.json()["detail"]


@pytest.mark.anyio
async def test_login_user_not_exists(async_client: AsyncClient):
    response = await async_client.post(
        "/token", json={"email": "noone@example.com", "password": "1234"}
    )
    assert response.status_code == 401

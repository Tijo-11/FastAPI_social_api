import pytest

from social_media_api import security


@pytest.mark.anyio
async def test_get_user(registered_user: dict):
    user = await security.get_user(registered_user["email"])

    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_get_user_not_found():
    user = await security.get_user("doesnotexist@example.com")
    assert user is None


@pytest.mark.anyio
async def test_password_hashes():
    password = "password123"
    hashed = security.get_password_hash(password)

    assert security.verify_password(password, hashed)

import pytest
from jose import jwt

from social_media_api import security


@pytest.mark.anyio
async def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


@pytest.mark.anyio
async def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


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


@pytest.mark.anyio
async def test_authenticate_user(registered_user: dict):
    user = await security.authenticate_user(
        registered_user["email"],
        registered_user["password"],
    )
    assert user.email == registered_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.net", "1234")


@pytest.mark.anyio
async def test_login_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrongpassword")

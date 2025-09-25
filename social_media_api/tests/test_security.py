import pytest
from jose import jwt

from social_media_api import security


# test access token
@pytest.mark.anyio
async def test_access_token_expire_minutes():
    assert security.access_token_expire_minutes() == 30


@pytest.mark.anyio
async def test_create_access_token():
    token = security.create_access_token("123")
    assert {"sub": "123", "type": "access"}.items() <= jwt.decode(
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
async def test_authenticate_user(confirmed_user: dict):
    user = await security.authenticate_user(
        confirmed_user["email"],
        confirmed_user["password"],
    )
    assert user.email == confirmed_user["email"]


@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(security.HTTPException):
        await security.authenticate_user("test@example.net", "1234")


@pytest.mark.anyio
async def test_login_wrong_password(registered_user: dict):
    with pytest.raises(security.HTTPException):
        await security.authenticate_user(registered_user["email"], "wrongpassword")


# Testing email confirmation token
@pytest.mark.anyio
async def test_confirmation_token_expire_minutes():
    assert security.confirm_token_expire_minutes() == 1440


@pytest.mark.anyio
async def test_create_confirmation_token():
    token = security.create_confirmation_token("123")
    assert {"sub": "123", "type": "confirmation"}.items() <= jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    ).items()


# ----testing wrong token received
@pytest.mark.anyio
async def test_get_current_user_wrong_type_token(registered_user: dict):
    token = security.create_confirmation_token(registered_user["email"])

    with pytest.raises(security.HTTPException):
        await security.get_current_user(token)


# ---testing data extraction from confiramtion token
@pytest.mark.anyio
async def test_get_subject_for_token_type_valid_confirmation():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    assert email == security.get_subject_for_token_type(token, "confirmation")


@pytest.mark.anyio
async def test_get_subject_for_token_type_valid_access():
    email = "test@example.com"
    token = security.create_access_token(email)
    assert email == security.get_subject_for_token_type(token, "access")


@pytest.mark.anyio
async def test_get_subject_for_token_type_expired(mocker):
    mocker.patch(
        "social_media_api.security.access_token_expire_minutes", return_value=-1
    )
    email = "test@example.com"
    token = security.create_access_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert "Token has expired" == exc_info.value.detail


@pytest.mark.anyio
async def test_get_subject_for_token_type_Invalid_token():
    token = "invalid token"
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")

    assert "Invalid Token" == exc_info.value.detail


# sub field missing
@pytest.mark.anyio
async def test_get_subject_for_token_type_missing_sub():
    email = "test@example.com"
    token = security.create_access_token(email)
    payload = jwt.decode(
        token, key=security.SECRET_KEY, algorithms=[security.ALGORITHM]
    )
    del payload["sub"]
    token = jwt.encode(payload, key=security.SECRET_KEY, algorithm=security.ALGORITHM)

    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token is missing 'sub'" <= exc_info.value.detail


# wrong type
@pytest.mark.anyio
async def test_get_subject_for_token_type_wrong_type():
    email = "test@example.com"
    token = security.create_confirmation_token(email)
    with pytest.raises(security.HTTPException) as exc_info:
        security.get_subject_for_token_type(token, "access")
    assert "Token has incorrect type" <= exc_info.value.detail

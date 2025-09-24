import logging

from fastapi import APIRouter, HTTPException, status

from social_media_api.database import database, user_table
from social_media_api.models.user import UserIn
from social_media_api.security import get_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", status_code=201)
async def register_user(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )
        # never store password as plain text, hash it
    query = user_table.insert().values(email=user.email, password=user.password)

    logger.debug(query)

    await database.execute(query)

    return {"detail": "User created"}

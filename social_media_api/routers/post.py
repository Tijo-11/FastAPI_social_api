import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from social_media_api.database import comments, database, likes_table, posts
from social_media_api.models.post import (
    Comment,
    CommentIn,
    PostLike,
    PostLikeIn,
    UserPost,
    UserPostIn,
    UserPostWithComments,
)
from social_media_api.models.user import User
from social_media_api.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)


async def find_post(post_id: int):
    logger.info(f"finding post with id {post_id}")
    query = posts.select().where(posts.c.id == post_id)  # sqlalchemy query
    logger.debug(query, extra={"email": "boban@example.com"})
    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(
    post: UserPostIn, current_user: Annotated[User, Depends(get_current_user)]
):
    logger.info("creating psot")

    data = {**post.model_dump(), "user_id": current_user.id}
    query = posts.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    logger.info("Getting all posts")
    query = posts.select()
    logger.debug(query)
    return await database.fetch_all(query)


@router.post("/comment", response_model=Comment, status_code=201)
async def create_comment(
    comment: CommentIn, current_user: Annotated[User, Depends(get_current_user)]
):
    post = await find_post(comment.post_id)
    if not post:
        logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post not found")

    data = {**comment.model_dump(), "user_id": current_user.id}
    query = comments.insert().values(data)
    last_record_id = await database.execute(query)
    new_comment = {**data, "id": last_record_id}
    return new_comment


@router.get("/post/{post_id}/comment", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = comments.select().where(comments.c.post_id == post_id)
    return await database.fetch_all(query)


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {
        "post": post,
        "comments": await get_comments_on_post(post_id),
    }


# Define Likes endpoints
@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(
    like: PostLikeIn, current_user=Annotated[User, Depends(get_current_user)]
):
    logger.infor("Liking Post")
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")

    data = {**like.dict(), "user_id": current_user.id}
    query = likes_table.insert().values(data)

    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

# main.py
import logging
import os
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from social_media_api.database import database
from social_media_api.logging_conf import configure_logging  # Updated function name
from social_media_api.routers.post import router as post_router
from social_media_api.routers.user import router as user_router

print(f"Current working directory: {os.getcwd()}")

logger = logging.getLogger("social_media_api")  # Use the correct logger name


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()  # Updated function name
    logger.info("Hello World")
    await database.connect()
    print("Database connected")
    yield
    await database.disconnect()
    print("Database disconnected")


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)

app.include_router(post_router)
app.include_router(user_router)


@app.get("/test-db")
async def test_db():
    try:
        await database.execute("SELECT 1")
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {str(e)}"}


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exception):
    logger.error(f"HTTPException: {exception.status_code} {exception.detail}")
    return await http_exception_handler(request, exception)

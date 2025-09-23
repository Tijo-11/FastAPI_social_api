# main.py
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from social_media_api.database import database
from social_media_api.logging_conf import configure_logging  # Updated function name
from social_media_api.routers.post import router as post_router

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

app.include_router(post_router)


@app.get("/test-db")
async def test_db():
    try:
        await database.execute("SELECT 1")
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {str(e)}"}

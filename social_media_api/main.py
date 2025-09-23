# main.py
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from social_media_api.database import database
from social_media_api.routers.post import router as post_router

print(f"Current working directory: {os.getcwd()}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("Database connected")  # Debug print
    yield
    await database.disconnect()
    print("Database disconnected")  # Debug print


app = FastAPI(lifespan=lifespan)  # Assign lifespan to the app

app.include_router(post_router)


@app.get("/test-db")
async def test_db():
    try:
        await database.execute("SELECT 1")
        return {"message": "Database connection successful"}
    except Exception as e:
        return {"message": f"Database connection failed: {str(e)}"}

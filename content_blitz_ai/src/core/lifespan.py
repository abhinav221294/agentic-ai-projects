from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.memory.init_db import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Initializing database...")

    init_database()

    yield

    print("Application shutting down...")
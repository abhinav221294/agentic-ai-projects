from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.core.lifespan import lifespan
from src.web_app.api.routes import router as api_router
from src.auth.routes import router as auth_router
from src.core.config import CORS_ORIGINS
from fastapi.staticfiles import StaticFiles
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]
STATIC_DIR = BASE_DIR / "static"

print("Serving:", STATIC_DIR)

app = FastAPI(
    title="Content Blitz AI",
    description="Multi-Agent Content Generation Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount(
    "/static",
    StaticFiles(directory=str(STATIC_DIR)),
    name="static",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router)
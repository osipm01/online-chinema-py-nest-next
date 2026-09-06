# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from src.api.api import api_router
from src.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Закрываем соединения при завершении приложения
    yield
    await engine.dispose()


app = FastAPI(
    title="Video Service API",
    version="1.0.0",
    lifespan=lifespan
)

# Подключаем API роуты
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Hello! Go to /docs to see API documentation",
        "admin": "Admin panel available at /admin"
    }
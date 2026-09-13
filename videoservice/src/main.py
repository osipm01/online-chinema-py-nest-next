# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
# 1. Импортируем CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware

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

# 2. Настраиваем CORS для любых IP и доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает запросы с любых доменов и IP
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все HTTP-методы (GET, POST, PUT, DELETE и т.д.)
    allow_headers=["*"],  # Разрешает любые HTTP-заголовки
)

# Подключаем API роуты
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Hello! Go to /docs to see API documentation",
        "admin": "Admin panel available at /admin"
    }

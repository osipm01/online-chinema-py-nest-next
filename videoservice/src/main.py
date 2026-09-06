# src/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.api.api import api_router
from src.admin.admin import setup_admin
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

# Добавляем SessionMiddleware для работы сессий админки
app.add_middleware(
    SessionMiddleware,
    secret_key="your-secure-secret-key-here",  # Замените на надежный секретный ключ
    session_cookie="admin_session",
    max_age=3600  # 1 час
)

# Инициализация админки
setup_admin(app)

# Подключаем API роуты
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Hello! Go to /docs to see API documentation",
        "admin": "Admin panel available at /admin"
    }
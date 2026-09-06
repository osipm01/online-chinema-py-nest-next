# src/api/v1/api.py
from fastapi import APIRouter

from src.api.endpoints.category_router import router as category_router
from src.api.endpoints.media_router import router as media_router

api_router = APIRouter()
api_router.include_router(category_router)
api_router.include_router(media_router)
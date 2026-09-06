# src/api/v1/endpoints/category.py
from typing import List, Tuple
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

# Импортируем генератор сессии (клиента)
from src.core.database import get_async_db
# Импортируем мозг приложения
from src.services.category_service import category_service
# DTO для валидации
from src.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryRead,
    CategoryWithMediaRead,
    CategoryWithMediaCount
)

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "/create",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Создать категорию",
    description="Создание новой категории с проверкой уникальности имени"
)
async def create_new_category(
        category_in: CategoryCreate,
        db: AsyncSession = Depends(get_async_db)
):
    """Эндпоинт создания категории"""
    return await category_service.create_category(db=db, category_in=category_in)


@router.get(
    "/",
    response_model=List[CategoryRead],
    status_code=status.HTTP_200_OK,
    summary="Получить все категории",
    description="Возвращает список всех категорий"
)
async def get_categories(
        db: AsyncSession = Depends(get_async_db)
):
    """Получение всех категорий"""
    return await category_service.get_categories(db=db)


@router.get(
    "/with-count",
    response_model=List[CategoryWithMediaCount],
    status_code=status.HTTP_200_OK,
    summary="Получить категории с количеством медиа",
    description="Возвращает категории с указанием количества привязанных медиа"
)
async def get_categories_with_media_count(
        skip: int = Query(0, ge=0, description="Пропустить N элементов"),
        limit: int = Query(100, ge=1, le=100, description="Максимум элементов"),
        db: AsyncSession = Depends(get_async_db)
):
    """Получение категорий с количеством медиа"""
    result = await category_service.get_categories_with_media_count(
        db=db,
        skip=skip,
        limit=limit
    )

    # Преобразуем результат в нужный формат
    return [
        CategoryWithMediaCount(
            id=cat.id,
            name=cat.name,
            media_count=count
        )
        for cat, count in result
    ]


@router.get(
    "/{category_id}",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
    summary="Получить категорию по ID",
    description="Возвращает категорию по её идентификатору"
)
async def get_category_by_id(
        category_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    """Получение категории по ID"""
    return await category_service.get_category_by_id(db=db, category_id=category_id)


@router.get(
    "/{category_id}/media",
    response_model=CategoryWithMediaRead,
    status_code=status.HTTP_200_OK,
    summary="Получить категорию с медиа",
    description="Возвращает категорию со списком всех привязанных медиа"
)
async def get_category_with_media(
        category_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    """Получение категории с медиа"""
    return await category_service.get_category_with_media_details(
        db=db,
        category_id=category_id
    )


@router.put(
    "/{category_id}",
    response_model=CategoryRead,
    status_code=status.HTTP_200_OK,
    summary="Обновить категорию",
    description="Обновление информации о категории с проверкой уникальности имени"
)
async def update_category(
        category_id: int,
        category_in: CategoryUpdate,
        db: AsyncSession = Depends(get_async_db)
):
    """Обновление категории"""
    return await category_service.update_category(
        db=db,
        category_id=category_id,
        category_in=category_in
    )


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить категорию",
    description="Удаление категории по ID"
)
async def delete_category(
        category_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    """Удаление категории"""
    await category_service.delete_category(db=db, category_id=category_id)


@router.post(
    "/{category_id}/media/{media_id}",
    status_code=status.HTTP_200_OK,
    summary="Добавить медиа в категорию",
    description="Привязывает медиа к категории (Many-to-Many связь)"
)
async def add_media_to_category(
        category_id: int,
        media_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    """Добавление медиа в категорию"""
    await category_service.add_media_to_category(
        db=db,
        category_id=category_id,
        media_id=media_id
    )
    return {"message": "Медиа успешно добавлено в категорию", "success": True}


@router.delete(
    "/{category_id}/media/{media_id}",
    status_code=status.HTTP_200_OK,
    summary="Удалить медиа из категории",
    description="Отвязывает медиа от категории (удаление Many-to-Many связи)"
)
async def remove_media_from_category(
        category_id: int,
        media_id: int,
        db: AsyncSession = Depends(get_async_db)
):
    """Удаление медиа из категории"""
    await category_service.remove_media_from_category(
        db=db,
        category_id=category_id,
        media_id=media_id
    )
    return {"message": "Медиа успешно удалено из категории", "success": True}
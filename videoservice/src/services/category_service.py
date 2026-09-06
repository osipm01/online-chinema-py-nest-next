# src/services/category.py
from typing import List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.crud_category import category_crud
from src.crud.media_crud import media_crud
from src.schemas.category import CategoryCreate, CategoryUpdate
from src.model.model import Category


class CategoryService:

    async def create_category(self, db: AsyncSession, category_in: CategoryCreate) -> Category:
        """
        Бизнес-логика создания категории.
        Проверяет уникальность имени перед сохранением.
        """
        existing_category = await category_crud.get_by_name(db, name=category_in.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Категория с именем '{category_in.name}' уже существует."
            )

        # Если имя свободно, вызываем базовый метод .create(), унаследованный от CRUDBase
        return await category_crud.create(db, obj_in=category_in)

    async def get_category_by_id(self, db: AsyncSession, category_id: int) -> Category:
        """
        Получение категории по ID.
        Если категории нет — сразу выбрасывает 404 ошибку.
        """
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )
        return category

    async def get_category_with_media_details(self, db: AsyncSession, category_id: int) -> Category:
        """
        Получение категории вместе со всеми медиафайлами (Many-to-Many).
        """
        category = await category_crud.get_with_media(db, category_id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )
        return category

    async def get_categories(self, db: AsyncSession) -> List[Category]:
        """Получение всех категорий"""
        return await category_crud.get_all(db=db)

    async def get_categories_with_media_count(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tuple[Category, int]]:
        """Получение категорий с количеством медиа"""
        return await category_crud.get_all_with_media_count(db, skip=skip, limit=limit)

    async def update_category(
        self,
        db: AsyncSession,
        category_id: int,
        category_in: CategoryUpdate
    ) -> Category:
        """Обновление категории с проверкой уникальности имени"""
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )

        update_data = category_in.model_dump(exclude_unset=True)

        # Если меняется имя, проверяем уникальность
        if "name" in update_data and update_data["name"] != category.name:
            existing = await category_crud.get_by_name(db, name=update_data["name"])
            if existing and existing.id != category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Категория с именем '{update_data['name']}' уже существует."
                )

        # Применяем обновления
        for field, value in update_data.items():
            setattr(category, field, value)

        await db.commit()
        await db.refresh(category)
        return category

    async def delete_category(self, db: AsyncSession, category_id: int) -> None:
        """Удаление категории"""
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )

        await category_crud.remove(db, id=category_id)

    async def add_media_to_category(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int
    ) -> None:
        """Добавление медиа в категорию"""
        # Проверяем существование категории
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )

        # Проверяем существование медиа
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )

        # Проверяем, нет ли уже такой связи
        exists = await category_crud.check_media_exists(
            db,
            category_id=category_id,
            media_id=media_id
        )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Медиа уже привязано к этой категории."
            )

        await category_crud.add_media(db, category_id=category_id, media_id=media_id)

    async def remove_media_from_category(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int
    ) -> None:
        """Удаление медиа из категории"""
        # Проверяем существование связи
        exists = await category_crud.check_media_exists(
            db,
            category_id=category_id,
            media_id=media_id
        )
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Связь между категорией и медиа не найдена."
            )

        await category_crud.remove_media(db, category_id=category_id, media_id=media_id)

    async def get_media_ids_by_category(self, db: AsyncSession, category_id: int) -> List[int]:
        """Получение всех media_id для категории"""
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )

        return await category_crud.get_media_ids(db, category_id=category_id)


category_service = CategoryService()
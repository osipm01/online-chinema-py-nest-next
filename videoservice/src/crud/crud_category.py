from typing import Sequence, Optional, Tuple, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.model.model import Category, Media
from src.schemas.category import CategoryCreate


class CRUDCategory(CRUDBase[Category, CategoryCreate]):

    async def get_with_media(self, db: AsyncSession, category_id: int) -> Optional[Category]:
        """Получение категории сразу со всеми привязанными медиафайлами"""
        result = await db.execute(
            select(self.model)
            .where(self.model.id == category_id)
            .options(selectinload(self.model.media))  # Жадная загрузка связей Many-to-Many
        )
        return result.scalars().first()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Category]:
        """Поиск по уникальному имени"""
        result = await db.execute(
            select(self.model).where(self.model.name == name)
        )
        return result.scalars().first()

    async def get_all(self, db: AsyncSession) -> Sequence[Category]:
        """Получение всех категорий"""
        result = await db.execute(
            select(self.model)
            .order_by(self.model.name)  # Сортировка по имени
        )
        return result.scalars().all()

    async def get_all_with_media_count(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Tuple[Category, int]]:
        """Получение всех категорий с количеством медиа"""
        result = await db.execute(
            select(self.model, func.count(Media.id))
            .outerjoin(self.model.media)  # LEFT JOIN чтобы получить категории без медиа
            .group_by(self.model.id)
            .order_by(self.model.name)
            .offset(skip)
            .limit(limit)
        )
        return result.all()

    async def add_media(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int
    ) -> None:
        """Добавить медиа в категорию"""
        await db.execute(
            text(
                "INSERT INTO media_categories (media_id, category_id) "
                "VALUES (:media_id, :category_id) "
                "ON CONFLICT DO NOTHING"  # Игнорируем если связь уже существует
            ),
            {"media_id": media_id, "category_id": category_id}
        )
        await db.commit()

    async def remove_media(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int
    ) -> None:
        """Удалить медиа из категории"""
        await db.execute(
            text(
                "DELETE FROM media_categories "
                "WHERE media_id = :media_id AND category_id = :category_id"
            ),
            {"media_id": media_id, "category_id": category_id}
        )
        await db.commit()

    # src/crud/crud_category.py (исправление)
    async def check_media_exists(
            self,
            db: AsyncSession,
            category_id: int,
            media_id: int
    ) -> bool:
        """Проверить, существует ли связь между категорией и медиа"""
        from sqlalchemy import text

        result = await db.execute(
            text(
                "SELECT 1 FROM media_category "  # Исправлено название таблицы
                "WHERE media_id = :media_id AND category_id = :category_id"
            ),
            {"media_id": media_id, "category_id": category_id}
        )
        return result.scalar() is not None

    async def get_media_ids(self, db: AsyncSession, category_id: int) -> List[int]:
        """Получить все media_id для категории"""
        result = await db.execute(
            text(
                "SELECT media_id FROM media_categories "
                "WHERE category_id = :category_id"
            ),
            {"category_id": category_id}
        )
        return [row[0] for row in result.all()]


category_crud = CRUDCategory(Category)
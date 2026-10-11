from typing import Sequence, Optional, Tuple, List

from loguru import logger
from sqlalchemy import select, func, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.model.model import Category, Media
from src.schemas.category import CategoryCreate


class CRUDCategory(CRUDBase[Category, CategoryCreate]):

    # ==================== CRUD / GET ====================

    async def get_with_media(
        self, db: AsyncSession, category_id: int
    ) -> Optional[Category]:
        """Получение категории сразу со всеми привязанными медиафайлами"""
        try:
            result = await db.execute(
                select(self.model)
                .where(self.model.id == category_id)
                .options(selectinload(self.model.media))
            )
            category = result.scalars().first()
            if category is None:
                logger.warning(f"Категория с id={category_id} не найдена")
            else:
                logger.debug(
                    f"Категория id={category_id} получена с медиа "
                    f"({len(category.media)} шт.)"
                )
            return category
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении категории id={category_id} с медиа: {e}"
            )
            raise

    async def get_by_name(
        self, db: AsyncSession, name: str
    ) -> Optional[Category]:
        """Поиск по уникальному имени"""
        try:
            result = await db.execute(
                select(self.model).where(self.model.name == name)
            )
            category = result.scalars().first()
            if category is None:
                logger.debug(f"Категория с именем '{name}' не найдена")
            return category
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при поиске категории по имени '{name}': {e}"
            )
            raise

    async def get_all(self, db: AsyncSession) -> Sequence[Category]:
        """Получение всех категорий"""
        try:
            result = await db.execute(
                select(self.model).order_by(self.model.name)
            )
            categories = result.scalars().all()
            logger.debug(f"Получено категорий: {len(categories)}")
            return categories
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении списка категорий: {e}")
            raise

    async def get_all_with_media_count(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Tuple[Category, int]]:
        """Получение всех категорий с количеством медиа"""
        try:
            result = await db.execute(
                select(self.model, func.count(Media.id))
                .outerjoin(self.model.media)
                .group_by(self.model.id)
                .order_by(self.model.name)
                .offset(skip)
                .limit(limit)
            )
            rows = result.all()
            logger.debug(
                f"Получено категорий с медиа-счётчиком: {len(rows)} "
                f"(skip={skip}, limit={limit})"
            )
            return rows
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении категорий с количеством медиа: {e}"
            )
            raise

    # ==================== MEDIA LINKS ====================

    async def add_media(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int,
    ) -> None:
        """Добавить медиа в категорию (идемпотентно)"""
        try:
            await db.execute(
                text(
                    "INSERT INTO media_category (media_id, category_id) "
                    "VALUES (:media_id, :category_id) "
                    "ON CONFLICT DO NOTHING"
                ),
                {"media_id": media_id, "category_id": category_id},
            )
            await db.commit()
            logger.info(
                f"Медиа id={media_id} добавлено в категорию id={category_id}"
            )
        except IntegrityError as e:
            await db.rollback()
            logger.error(
                f"Нарушение целостности при добавлении медиа id={media_id} "
                f"в категорию id={category_id} (неверный id?): {e}"
            )
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(
                f"Ошибка БД при добавлении медиа id={media_id} "
                f"в категорию id={category_id}: {e}"
            )
            raise

    async def remove_media(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int,
    ) -> None:
        """Удалить медиа из категории"""
        try:
            result = await db.execute(
                text(
                    "DELETE FROM media_category "
                    "WHERE media_id = :media_id AND category_id = :category_id"
                ),
                {"media_id": media_id, "category_id": category_id},
            )
            await db.commit()
            if result.rowcount == 0:
                logger.warning(
                    f"Связь медиа id={media_id} с категорией id={category_id} "
                    f"не найдена — нечего удалять"
                )
            else:
                logger.info(
                    f"Медиа id={media_id} удалено из категории id={category_id}"
                )
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(
                f"Ошибка БД при удалении медиа id={media_id} "
                f"из категории id={category_id}: {e}"
            )
            raise

    async def check_media_exists(
        self,
        db: AsyncSession,
        category_id: int,
        media_id: int,
    ) -> bool:
        """Проверить, существует ли связь между категорией и медиа"""
        try:
            result = await db.execute(
                text(
                    "SELECT 1 FROM media_category "
                    "WHERE media_id = :media_id AND category_id = :category_id"
                ),
                {"media_id": media_id, "category_id": category_id},
            )
            exists = result.scalar() is not None
            logger.debug(
                f"Проверка связи медиа id={media_id} ↔ категория "
                f"id={category_id}: {exists}"
            )
            return exists
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при проверке связи медиа id={media_id} "
                f"и категории id={category_id}: {e}"
            )
            raise

    async def get_media_ids(
        self, db: AsyncSession, category_id: int
    ) -> List[int]:
        """Получить все media_id для категории"""
        try:
            result = await db.execute(
                text(
                    "SELECT media_id FROM media_category "
                    "WHERE category_id = :category_id"
                ),
                {"category_id": category_id},
            )
            ids = [row[0] for row in result.all()]
            logger.debug(
                f"Для категории id={category_id} найдено media_id: {len(ids)}"
            )
            return ids
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении media_id для категории "
                f"id={category_id}: {e}"
            )
            raise

    # ==================== CASCADE DELETE ====================

    async def cascade_delete_category(
        self, db: AsyncSession, category_id: int
    ) -> None:
        """
        Каскадное удаление категории:
        1. Проверяет существование.
        2. Удаляет связи в media_category.
        3. Удаляет саму категорию.
        """
        try:
            category = await self.get(db, category_id)
            if category is None:
                logger.warning(
                    f"Каскадное удаление пропущено: категория id={category_id} "
                    f"не найдена"
                )
                return

            result = await db.execute(
                text(
                    "DELETE FROM media_category "
                    "WHERE category_id = :category_id"
                ),
                {"category_id": category_id},
            )
            links_deleted = result.rowcount or 0
            logger.debug(
                f"Удалено связей media_category для категории id={category_id}: "
                f"{links_deleted}"
            )

            await db.delete(category)
            await db.commit()

            logger.info(
                f"Категория id={category_id} каскадно удалена "
                f"(связей удалено: {links_deleted})"
            )
        except IntegrityError as e:
            await db.rollback()
            logger.error(
                f"Нарушение целостности при каскадном удалении категории "
                f"id={category_id}: {e}"
            )
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(
                f"Ошибка БД при каскадном удалении категории "
                f"id={category_id}: {e}"
            )
            raise


category_crud = CRUDCategory(Category)
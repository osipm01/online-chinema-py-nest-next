from typing import Sequence, Optional, List, Tuple
from sqlalchemy import select, func, or_, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.model.model import Media, Season, Episode, Category
from src.schemas.media import MediaCreate


class CRUDMedia(CRUDBase[Media, MediaCreate]):

    async def get_full_details(self, db: AsyncSession, media_id: int) -> Optional[Media]:
        """
        Получить медиа со всеми вложенными зависимостями:
        - Если это сериал: подгружаются сезоны и серии внутри каждого сезона.
        - Если это фильм: подгружаются прямые серии.
        - Также подгружаются категории.
        """
        result = await db.execute(
            select(self.model)
            .where(self.model.id == media_id)
            .options(
                selectinload(self.model.categories),
                selectinload(self.model.seasons).selectinload(Season.episodes),
                selectinload(self.model.episodes)
            )
        )
        return result.scalars().first()

    async def get_movies(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Media]:
        """Получить только фильмы с пагинацией"""
        result = await db.execute(
            select(self.model)
            .where(self.model.type == "movie")
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_tv_shows(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Sequence[Media]:
        """Получить только сериалы с пагинацией"""
        result = await db.execute(
            select(self.model)
            .where(self.model.type == "tv_show")
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_category(self, db: AsyncSession, category_id: int, skip: int = 0, limit: int = 100) -> Sequence[
        Media]:
        """Получить все медиа-ресурсы, принадлежащие определенной категории"""
        result = await db.execute(
            select(self.model)
            .join(self.model.categories)
            .where(Category.id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search(self, db: AsyncSession, query: str, skip: int = 0, limit: int = 100) -> Sequence[Media]:
        """Поиск медиа по названию или описанию"""
        result = await db.execute(
            select(self.model)
            .where(
                or_(
                    self.model.title.ilike(f"%{query}%"),
                    self.model.description.ilike(f"%{query}%")
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_recent(self, db: AsyncSession, limit: int = 10) -> Sequence[Media]:
        """Получить последние добавленные медиа"""
        result = await db.execute(
            select(self.model)
            .order_by(self.model.id.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def get_media_with_categories(self, db: AsyncSession, media_id: int) -> Optional[Media]:
        """Получить медиа только с категориями"""
        result = await db.execute(
            select(self.model)
            .where(self.model.id == media_id)
            .options(
                selectinload(self.model.categories)
            )
        )
        return result.scalars().first()

    async def update_categories(self, db: AsyncSession, media_id: int, category_ids: List[int]) -> Optional[Media]:
        """Обновить категории для медиа"""
        media = await self.get(db, media_id)
        if not media:
            return None

        # Удаляем старые связи
        await db.execute(
            text("DELETE FROM media_categories WHERE media_id = :media_id"),
            {"media_id": media_id}
        )

        # Добавляем новые
        for category_id in category_ids:
            await db.execute(
                text("INSERT INTO media_categories (media_id, category_id) VALUES (:media_id, :category_id)"),
                {"media_id": media_id, "category_id": category_id}
            )

        await db.commit()

        # Возвращаем обновленное медиа с категориями
        return await self.get_media_with_categories(db, media_id)

    # ==================== SEASON METHODS ====================

    async def get_seasons_by_media(self, db: AsyncSession, media_id: int) -> Sequence[Season]:
        """Получить все сезоны сериала"""
        result = await db.execute(
            select(Season)
            .where(Season.media_id == media_id)
            .order_by(Season.season_number)
        )
        return result.scalars().all()

    async def get_season_with_episodes(self, db: AsyncSession, season_id: int) -> Optional[Season]:
        """Получить сезон со всеми эпизодами"""
        result = await db.execute(
            select(Season)
            .where(Season.id == season_id)
            .options(
                selectinload(Season.episodes),
                selectinload(Season.media)
            )
        )
        return result.scalars().first()

    async def get_season_by_number(self, db: AsyncSession, media_id: int, season_number: int) -> Optional[Season]:
        """Получить конкретный сезон по номеру"""
        result = await db.execute(
            select(Season)
            .where(
                Season.media_id == media_id,
                Season.season_number == season_number
            )
        )
        return result.scalars().first()

    # ==================== EPISODE METHODS ====================

    async def get_episodes_by_season(self, db: AsyncSession, season_id: int) -> Sequence[Episode]:
        """Получить все эпизоды сезона"""
        result = await db.execute(
            select(Episode)
            .where(Episode.season_id == season_id)
            .order_by(Episode.id)
        )
        return result.scalars().all()

    async def get_episodes_by_media(self, db: AsyncSession, media_id: int) -> Sequence[Episode]:
        """Получить прямые эпизоды фильма"""
        result = await db.execute(
            select(Episode)
            .where(Episode.media_id == media_id)
            .order_by(Episode.id)
        )
        return result.scalars().all()

    async def get_episode_with_details(self, db: AsyncSession, episode_id: int) -> Optional[Episode]:
        """Получить эпизод с информацией о сезоне и медиа"""
        result = await db.execute(
            select(Episode)
            .where(Episode.id == episode_id)
            .options(
                selectinload(Episode.season),
                selectinload(Episode.media)
            )
        )
        return result.scalars().first()

    # ==================== CATEGORY METHODS ====================

    async def get_category_with_media(self, db: AsyncSession, category_id: int) -> Optional[Category]:
        """Получить категорию со всеми медиа-ресурсами"""
        result = await db.execute(
            select(Category)
            .where(Category.id == category_id)
            .options(
                selectinload(Category.media)
            )
        )
        return result.scalars().first()

    async def get_category_by_name(self, db: AsyncSession, name: str) -> Optional[Category]:
        """Найти категорию по имени"""
        result = await db.execute(
            select(Category)
            .where(Category.name == name)
        )
        return result.scalars().first()

    async def get_all_categories_with_media_count(self, db: AsyncSession) -> Sequence[Tuple[Category, int]]:
        """Получить все категории с количеством медиа"""
        result = await db.execute(
            select(Category, func.count(Media.id))
            .join(Category.media)
            .group_by(Category.id)
        )
        return result.all()

    async def add_media_to_category(self, db: AsyncSession, category_id: int, media_id: int) -> None:
        """Добавить медиа в категорию"""
        await db.execute(
            text("INSERT INTO media_categories (media_id, category_id) VALUES (:media_id, :category_id)"),
            {"media_id": media_id, "category_id": category_id}
        )
        await db.commit()

    async def remove_media_from_category(self, db: AsyncSession, category_id: int, media_id: int) -> None:
        """Удалить медиа из категории"""
        await db.execute(
            text("DELETE FROM media_categories WHERE media_id = :media_id AND category_id = :category_id"),
            {"media_id": media_id, "category_id": category_id}
        )
        await db.commit()


media_crud = CRUDMedia(Media)
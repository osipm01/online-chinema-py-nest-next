from typing import Sequence, Optional, List, Tuple

from loguru import logger
from sqlalchemy import select, func, or_, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.model.model import Media, Season, Episode, Category
from src.schemas.media import MediaCreate


class CRUDMedia(CRUDBase[Media, MediaCreate]):

    # ==================== MEDIA METHODS ====================

    async def get_full_details(self, db: AsyncSession, media_id: int) -> Optional[Media]:
        """
        Получить медиа со всеми вложенными зависимостями:
        - Если это сериал: подгружаются сезоны и серии внутри каждого сезона.
        - Если это фильм: подгружаются прямые серии.
        - Также подгружаются категории.
        """
        try:
            result = await db.execute(
                select(self.model)
                .where(self.model.id == media_id)
                .options(
                    selectinload(self.model.categories),
                    selectinload(self.model.seasons).selectinload(Season.episodes),
                    selectinload(self.model.episodes),
                )
            )
            media = result.scalars().first()
            if media is None:
                logger.warning(f"Медиа с id={media_id} не найдено (full details)")
            else:
                logger.debug(
                    f"Медиа id={media_id} получено: "
                    f"категорий={len(media.categories)}, "
                    f"сезонов={len(media.seasons)}, "
                    f"прямых эпизодов={len(media.episodes)}"
                )
            return media
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении полных данных медиа id={media_id}: {e}")
            raise

    async def get_movies(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Media]:
        """Получить только фильмы с пагинацией"""
        try:
            result = await db.execute(
                select(self.model)
                .where(self.model.type == "movie")
                .offset(skip)
                .limit(limit)
            )
            movies = result.scalars().all()
            logger.debug(f"Получено фильмов: {len(movies)} (skip={skip}, limit={limit})")
            return movies
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении фильмов (skip={skip}, limit={limit}): {e}")
            raise

    async def get_tv_shows(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Media]:
        """Получить только сериалы с пагинацией"""
        try:
            result = await db.execute(
                select(self.model)
                .where(self.model.type == "tv_show")
                .offset(skip)
                .limit(limit)
            )
            shows = result.scalars().all()
            logger.debug(f"Получено сериалов: {len(shows)} (skip={skip}, limit={limit})")
            return shows
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении сериалов (skip={skip}, limit={limit}): {e}")
            raise

    async def get_by_category(
        self,
        db: AsyncSession,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Media]:
        """Получить все медиа-ресурсы, принадлежащие определенной категории"""
        try:
            result = await db.execute(
                select(self.model)
                .join(self.model.categories)
                .where(Category.id == category_id)
                .offset(skip)
                .limit(limit)
            )
            media_list = result.scalars().all()
            logger.debug(
                f"Получено медиа для категории id={category_id}: "
                f"{len(media_list)} (skip={skip}, limit={limit})"
            )
            return media_list
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении медиа для категории id={category_id}: {e}"
            )
            raise

    async def search(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Media]:
        """Поиск медиа по названию или описанию"""
        try:
            result = await db.execute(
                select(self.model)
                .where(
                    or_(
                        self.model.title.ilike(f"%{query}%"),
                        self.model.description.ilike(f"%{query}%"),
                    )
                )
                .offset(skip)
                .limit(limit)
            )
            media_list = result.scalars().all()
            logger.debug(
                f"Поиск '{query}' дал {len(media_list)} результатов "
                f"(skip={skip}, limit={limit})"
            )
            return media_list
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при поиске медиа по запросу '{query}': {e}")
            raise

    async def get_recent(self, db: AsyncSession, limit: int = 10) -> Sequence[Media]:
        """Получить последние добавленные медиа"""
        try:
            result = await db.execute(
                select(self.model)
                .order_by(self.model.id.desc())
                .limit(limit)
            )
            media_list = result.scalars().all()
            logger.debug(f"Получено последних медиа: {len(media_list)} (limit={limit})")
            return media_list
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении последних медиа: {e}")
            raise

    async def get_media_with_categories(
        self, db: AsyncSession, media_id: int
    ) -> Optional[Media]:
        """Получить медиа только с категориями"""
        try:
            result = await db.execute(
                select(self.model)
                .where(self.model.id == media_id)
                .options(selectinload(self.model.categories))
            )
            media = result.scalars().first()
            if media is None:
                logger.warning(f"Медиа с id={media_id} не найдено (with categories)")
            return media
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении медиа id={media_id} с категориями: {e}"
            )
            raise

    async def update_categories(
        self,
        db: AsyncSession,
        media_id: int,
        category_ids: List[int],
    ) -> Optional[Media]:
        """Обновить категории для медиа"""
        try:
            media = await self.get(db, media_id)
            if not media:
                logger.warning(
                    f"Невозможно обновить категории: медиа id={media_id} не найдено"
                )
                return None

            # Удаляем старые связи
            await db.execute(
                text("DELETE FROM media_category WHERE media_id = :media_id"),
                {"media_id": media_id},
            )

            # Добавляем новые
            for category_id in category_ids:
                await db.execute(
                    text(
                        "INSERT INTO media_category (media_id, category_id) "
                        "VALUES (:media_id, :category_id)"
                    ),
                    {"media_id": media_id, "category_id": category_id},
                )

            await db.commit()
            logger.info(
                f"Обновлены категории для медиа id={media_id}: "
                f"установлено {len(category_ids)} связей"
            )

            return await self.get_media_with_categories(db, media_id)

        except IntegrityError as e:
            await db.rollback()
            logger.error(
                f"Нарушение целостности при обновлении категорий медиа id={media_id} "
                f"(category_ids={category_ids}): {e}"
            )
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(
                f"Ошибка БД при обновлении категорий медиа id={media_id}: {e}"
            )
            raise

    # ==================== SEASON METHODS ====================

    async def get_seasons_by_media(
        self, db: AsyncSession, media_id: int
    ) -> Sequence[Season]:
        """Получить все сезоны сериала"""
        try:
            result = await db.execute(
                select(Season)
                .where(Season.media_id == media_id)
                .order_by(Season.season_number)
            )
            seasons = result.scalars().all()
            logger.debug(f"Получено сезонов для медиа id={media_id}: {len(seasons)}")
            return seasons
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении сезонов медиа id={media_id}: {e}")
            raise

    async def get_season_with_episodes(
        self, db: AsyncSession, season_id: int
    ) -> Optional[Season]:
        """Получить сезон со всеми эпизодами"""
        try:
            result = await db.execute(
                select(Season)
                .where(Season.id == season_id)
                .options(
                    selectinload(Season.episodes),
                    selectinload(Season.media),
                )
            )
            season = result.scalars().first()
            if season is None:
                logger.warning(f"Сезон с id={season_id} не найден")
            else:
                logger.debug(
                    f"Сезон id={season_id} получен: эпизодов={len(season.episodes)}"
                )
            return season
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении сезона id={season_id}: {e}")
            raise

    async def get_season_by_number(
        self, db: AsyncSession, media_id: int, season_number: int
    ) -> Optional[Season]:
        """Получить конкретный сезон по номеру"""
        try:
            result = await db.execute(
                select(Season).where(
                    Season.media_id == media_id,
                    Season.season_number == season_number,
                )
            )
            season = result.scalars().first()
            if season is None:
                logger.debug(
                    f"Сезон {season_number} медиа id={media_id} не найден"
                )
            return season
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении сезона {season_number} "
                f"медиа id={media_id}: {e}"
            )
            raise

    # ==================== EPISODE METHODS ====================

    async def get_episodes_by_season(
        self, db: AsyncSession, season_id: int
    ) -> Sequence[Episode]:
        """Получить все эпизоды сезона"""
        try:
            result = await db.execute(
                select(Episode)
                .where(Episode.season_id == season_id)
                .order_by(Episode.id)
            )
            episodes = result.scalars().all()
            logger.debug(f"Получено эпизодов сезона id={season_id}: {len(episodes)}")
            return episodes
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении эпизодов сезона id={season_id}: {e}")
            raise

    async def get_episodes_by_media(
        self, db: AsyncSession, media_id: int
    ) -> Sequence[Episode]:
        """Получить прямые эпизоды фильма"""
        try:
            result = await db.execute(
                select(Episode)
                .where(Episode.media_id == media_id)
                .order_by(Episode.id)
            )
            episodes = result.scalars().all()
            logger.debug(f"Получено прямых эпизодов медиа id={media_id}: {len(episodes)}")
            return episodes
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении прямых эпизодов медиа id={media_id}: {e}"
            )
            raise

    async def get_episode_with_details(
        self, db: AsyncSession, episode_id: int
    ) -> Optional[Episode]:
        """Получить эпизод с информацией о сезоне и медиа"""
        try:
            result = await db.execute(
                select(Episode)
                .where(Episode.id == episode_id)
                .options(
                    selectinload(Episode.season),
                    selectinload(Episode.media),
                )
            )
            episode = result.scalars().first()
            if episode is None:
                logger.warning(f"Эпизод с id={episode_id} не найден")
            return episode
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при получении эпизода id={episode_id}: {e}")
            raise

    # ==================== CATEGORY METHODS ====================

    async def get_category_with_media(
        self, db: AsyncSession, category_id: int
    ) -> Optional[Category]:
        """Получить категорию со всеми медиа-ресурсами"""
        try:
            result = await db.execute(
                select(Category)
                .where(Category.id == category_id)
                .options(selectinload(Category.media))
            )
            category = result.scalars().first()
            if category is None:
                logger.warning(f"Категория с id={category_id} не найдена")
            else:
                logger.debug(
                    f"Категория id={category_id} получена: медиа={len(category.media)}"
                )
            return category
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении категории id={category_id} с медиа: {e}"
            )
            raise

    async def get_category_by_name(
        self, db: AsyncSession, name: str
    ) -> Optional[Category]:
        """Найти категорию по имени"""
        try:
            result = await db.execute(
                select(Category).where(Category.name == name)
            )
            category = result.scalars().first()
            if category is None:
                logger.debug(f"Категория с именем '{name}' не найдена")
            return category
        except SQLAlchemyError as e:
            logger.exception(f"Ошибка БД при поиске категории '{name}': {e}")
            raise

    async def get_all_categories_with_media_count(
        self, db: AsyncSession
    ) -> Sequence[Tuple[Category, int]]:
        """Получить все категории с количеством медиа"""
        try:
            result = await db.execute(
                select(Category, func.count(Media.id))
                .join(Category.media)
                .group_by(Category.id)
            )
            rows = result.all()
            logger.debug(f"Получено категорий со счётчиком медиа: {len(rows)}")
            return rows
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении категорий с количеством медиа: {e}"
            )
            raise

    async def add_media_to_category(
        self, db: AsyncSession, category_id: int, media_id: int
    ) -> None:
        """Добавить медиа в категорию"""
        try:
            await db.execute(
                text(
                    "INSERT INTO media_category (media_id, category_id) "
                    "VALUES (:media_id, :category_id)"
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
                f"в категорию id={category_id} "
                f"(возможно, связь уже существует или неверный id): {e}"
            )
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(
                f"Ошибка БД при добавлении медиа id={media_id} "
                f"в категорию id={category_id}: {e}"
            )
            raise

    async def remove_media_from_category(
        self, db: AsyncSession, category_id: int, media_id: int
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


media_crud = CRUDMedia(Media)
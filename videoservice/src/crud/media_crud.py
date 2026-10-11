from typing import Sequence, Optional, List

from loguru import logger
from sqlalchemy import select, or_, text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.crud.base import CRUDBase
from src.model.model import Media, Season, Episode
from src.schemas.media import MediaCreate


class CRUDMedia(CRUDBase[Media, MediaCreate]):

    # ==================== MEDIA ====================

    async def get_full_details(
        self, db: AsyncSession, media_id: int
    ) -> Optional[Media]:
        """
        Получить медиа со всеми вложенными зависимостями:
        - сериал: сезоны + эпизоды внутри сезонов;
        - фильм: прямые эпизоды;
        - категории.
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
                logger.warning(
                    f"Медиа с id={media_id} не найдено (full details)"
                )
            else:
                logger.debug(
                    f"Медиа id={media_id} получено: "
                    f"категорий={len(media.categories)}, "
                    f"сезонов={len(media.seasons)}, "
                    f"прямых эпизодов={len(media.episodes)}"
                )
            return media
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении полных данных медиа "
                f"id={media_id}: {e}"
            )
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
            logger.debug(
                f"Получено фильмов: {len(movies)} (skip={skip}, limit={limit})"
            )
            return movies
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении фильмов "
                f"(skip={skip}, limit={limit}): {e}"
            )
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
            logger.debug(
                f"Получено сериалов: {len(shows)} (skip={skip}, limit={limit})"
            )
            return shows
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении сериалов "
                f"(skip={skip}, limit={limit}): {e}"
            )
            raise

    async def get_by_category(
        self,
        db: AsyncSession,
        category_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Media]:
        """Получить все медиа, принадлежащие категории"""
        try:
            result = await db.execute(
                select(self.model)
                .join(self.model.categories)
                .where(self.model.categories.any(id=category_id))
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
                f"Ошибка БД при получении медиа для категории "
                f"id={category_id}: {e}"
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
            logger.exception(
                f"Ошибка БД при поиске медиа по запросу '{query}': {e}"
            )
            raise

    async def get_recent(
        self, db: AsyncSession, limit: int = 10
    ) -> Sequence[Media]:
        """Получить последние добавленные медиа"""
        try:
            result = await db.execute(
                select(self.model)
                .order_by(self.model.id.desc())
                .limit(limit)
            )
            media_list = result.scalars().all()
            logger.debug(
                f"Получено последних медиа: {len(media_list)} (limit={limit})"
            )
            return media_list
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении последних медиа: {e}"
            )
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
                logger.warning(
                    f"Медиа с id={media_id} не найдено (with categories)"
                )
            return media
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении медиа id={media_id} "
                f"с категориями: {e}"
            )
            raise

    async def update_categories(
        self,
        db: AsyncSession,
        media_id: int,
        category_ids: List[int],
    ) -> Optional[Media]:
        """
        Полностью заменить набор категорий у медиа.

        Семантически это операция над медиа («у этого медиа теперь
        такие категории»), поэтому метод живёт здесь. За добавление/
        удаление одной связи отвечает CRUDCategory.
        """
        try:
            media = await self.get(db, media_id)
            if not media:
                logger.warning(
                    f"Невозможно обновить категории: медиа id={media_id} "
                    f"не найдено"
                )
                return None

            await db.execute(
                text("DELETE FROM media_category WHERE media_id = :media_id"),
                {"media_id": media_id},
            )

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
                f"Нарушение целостности при обновлении категорий медиа "
                f"id={media_id} (category_ids={category_ids}): {e}"
            )
            raise
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(
                f"Ошибка БД при обновлении категорий медиа id={media_id}: {e}"
            )
            raise

    # ==================== SEASONS ====================

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
            logger.debug(
                f"Получено сезонов для медиа id={media_id}: {len(seasons)}"
            )
            return seasons
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении сезонов медиа id={media_id}: {e}"
            )
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
                    f"Сезон id={season_id} получен: "
                    f"эпизодов={len(season.episodes)}"
                )
            return season
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении сезона id={season_id}: {e}"
            )
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

    # ==================== EPISODES ====================

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
            logger.debug(
                f"Получено эпизодов сезона id={season_id}: {len(episodes)}"
            )
            return episodes
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении эпизодов сезона "
                f"id={season_id}: {e}"
            )
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
            logger.debug(
                f"Получено прямых эпизодов медиа id={media_id}: "
                f"{len(episodes)}"
            )
            return episodes
        except SQLAlchemyError as e:
            logger.exception(
                f"Ошибка БД при получении прямых эпизодов медиа "
                f"id={media_id}: {e}"
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
            logger.exception(
                f"Ошибка БД при получении эпизода id={episode_id}: {e}"
            )
            raise


media_crud = CRUDMedia(Media)
# src/services/media.py
from typing import List

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.crud_category import category_crud
from src.crud.media_crud import media_crud
from src.model.model import Media, Category, Season, Episode
from src.schemas.media import (
    MediaCreate,
    MediaUpdate,
    EpisodeCreate,
    SeasonCreate,
)


class MediaService:

    # ==================== MEDIA ====================

    async def create_media(
        self, db: AsyncSession, media_in: MediaCreate
    ) -> Media:
        """
        Создание медиа.
        - Проверяет, что все указанные категории существуют.
        - Привязывает их через M2M.
        """
        category_ids = media_in.category_ids or []
        media_data = media_in.model_dump(exclude={"category_ids"})

        # Готовим объект
        db_obj = Media(**media_data)

        # Привязываем категории (если переданы)
        if category_ids:
            result = await db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            categories = result.scalars().all()

            if len(categories) != len(category_ids):
                found_ids = {c.id for c in categories}
                missing = set(category_ids) - found_ids
                logger.warning(
                    f"Создание медиа: не найдены категории {missing}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Одна или несколько указанных категорий "
                        "не найдены."
                    ),
                )

            db_obj.categories = list(categories)

        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(
                f"Медиа создано: id={db_obj.id}, "
                f"категорий={len(category_ids)}"
            )
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.exception(f"Ошибка при создании медиа: {e}")
            raise

    async def get_media_by_id(
        self, db: AsyncSession, media_id: int
    ) -> Media:
        """Базовая информация о медиа (без связей)."""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден.",
            )
        return media

    async def get_media_with_relations(
        self, db: AsyncSession, media_id: int
    ) -> Media:
        """Медиа со всей структурой (категории, сезоны, эпизоды)."""
        media = await media_crud.get_full_details(db, media_id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден.",
            )
        return media

    async def get_all_movies(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ):
        """Список только фильмов"""
        return await media_crud.get_movies(db, skip=skip, limit=limit)

    async def get_all_tv_shows(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ):
        """Список только сериалов"""
        return await media_crud.get_tv_shows(db, skip=skip, limit=limit)

    async def get_media_by_category_id(
        self, db: AsyncSession, category_id: int
    ):
        """Список медиа по категории"""
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена.",
            )
        return await media_crud.get_by_category(
            db, category_id=category_id
        )

    async def search_media(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100,
    ):
        """Поиск медиа по названию или описанию"""
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поисковый запрос не может быть пустым.",
            )
        return await media_crud.search(
            db, query=query, skip=skip, limit=limit
        )

    async def get_recent_media(self, db: AsyncSession, limit: int = 10):
        """Последние добавленные медиа"""
        return await media_crud.get_recent(db, limit=limit)

    async def update_media(
        self,
        db: AsyncSession,
        media_id: int,
        media_in: MediaUpdate,
    ) -> Media:
        """Обновление медиа (включая замену категорий)"""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден.",
            )

        update_data = media_in.model_dump(exclude_unset=True)

        # Обновление категорий (полная замена набора)
        if "category_ids" in update_data:
            category_ids = update_data.pop("category_ids")
            if category_ids is not None:
                await media_crud.update_categories(
                    db, media_id, category_ids
                )

        # Обновление скалярных полей
        if update_data:
            for field, value in update_data.items():
                setattr(media, field, value)
            try:
                await db.commit()
                await db.refresh(media)
                logger.info(f"Медиа id={media_id} обновлено")
            except Exception as e:
                await db.rollback()
                logger.exception(
                    f"Ошибка при обновлении медиа id={media_id}: {e}"
                )
                raise

        return media

    async def delete_media(
        self, db: AsyncSession, media_id: int
    ) -> None:
        """Удаление медиа"""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден.",
            )

        try:
            await media_crud.remove(db, id=media_id)
            logger.info(f"Медиа id={media_id} удалено")
        except Exception as e:
            logger.exception(
                f"Ошибка при удалении медиа id={media_id}: {e}"
            )
            raise

    # ==================== SEASONS ====================

    async def create_season(
        self, db: AsyncSession, season_in: SeasonCreate
    ) -> Season:
        """Создание сезона с проверками"""
        media = await media_crud.get(db, id=season_in.media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден.",
            )

        if media.type != "tv_show":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сезоны можно добавлять только к сериалам.",
            )

        existing_season = await media_crud.get_season_by_number(
            db,
            media_id=season_in.media_id,
            season_number=season_in.season_number,
        )
        if existing_season:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Сезон с номером {season_in.season_number} "
                    f"уже существует."
                ),
            )

        db_obj = Season(**season_in.model_dump())
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(
                f"Сезон создан: id={db_obj.id}, "
                f"медиа id={season_in.media_id}, "
                f"номер={season_in.season_number}"
            )
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.exception(f"Ошибка при создании сезона: {e}")
            raise

    async def get_seasons_by_media(
        self, db: AsyncSession, media_id: int
    ) -> List[Season]:
        """Все сезоны сериала"""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден.",
            )
        return await media_crud.get_seasons_by_media(
            db, media_id=media_id
        )

    async def get_season_with_episodes(
        self, db: AsyncSession, season_id: int
    ) -> Season:
        """Сезон со всеми эпизодами"""
        season = await media_crud.get_season_with_episodes(
            db, season_id=season_id
        )
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден.",
            )
        return season

    async def update_season(
        self, db: AsyncSession, season_id: int, season_in: dict
    ) -> Season:
        """Обновление сезона"""
        season = await media_crud.get_season_with_episodes(
            db, season_id=season_id
        )
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден.",
            )

        for field, value in season_in.items():
            setattr(season, field, value)

        try:
            await db.commit()
            await db.refresh(season)
            logger.info(f"Сезон id={season_id} обновлён")
        except Exception as e:
            await db.rollback()
            logger.exception(
                f"Ошибка при обновлении сезона id={season_id}: {e}"
            )
            raise
        return season

    async def delete_season(
        self, db: AsyncSession, season_id: int
    ) -> None:
        """Удаление сезона"""
        season = await media_crud.get_season_with_episodes(
            db, season_id=season_id
        )
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден.",
            )

        try:
            await db.delete(season)
            await db.commit()
            logger.info(f"Сезон id={season_id} удалён")
        except Exception as e:
            await db.rollback()
            logger.exception(
                f"Ошибка при удалении сезона id={season_id}: {e}"
            )
            raise

    # ==================== EPISODES ====================

    async def create_episode(
        self, db: AsyncSession, episode_in: EpisodeCreate
    ) -> Episode:
        """Создание эпизода с проверками"""
        if episode_in.season_id is None and episode_in.media_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Эпизод должен быть привязан к сезону или медиа.",
            )

        if episode_in.season_id:
            season = await media_crud.get_season_with_episodes(
                db, season_id=episode_in.season_id
            )
            if not season:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Сезон не найден.",
                )

        if episode_in.media_id:
            media = await media_crud.get(db, id=episode_in.media_id)
            if not media:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Медиаресурс не найден.",
                )

            if media.type == "tv_show" and not episode_in.season_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Эпизоды сериала должны быть привязаны к сезону."
                    ),
                )

        db_obj = Episode(**episode_in.model_dump())
        try:
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f"Эпизод создан: id={db_obj.id}")
            return db_obj
        except Exception as e:
            await db.rollback()
            logger.exception(f"Ошибка при создании эпизода: {e}")
            raise

    async def get_episodes_by_season(
        self, db: AsyncSession, season_id: int
    ) -> List[Episode]:
        """Все эпизоды сезона"""
        season = await media_crud.get_season_with_episodes(
            db, season_id=season_id
        )
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден.",
            )
        return await media_crud.get_episodes_by_season(
            db, season_id=season_id
        )

    async def get_episode_with_details(
        self, db: AsyncSession, episode_id: int
    ) -> Episode:
        """Эпизод с информацией о родителях"""
        episode = await media_crud.get_episode_with_details(
            db, episode_id=episode_id
        )
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Эпизод не найден.",
            )
        return episode

    async def update_episode(
        self, db: AsyncSession, episode_id: int, episode_in: dict
    ) -> Episode:
        """Обновление эпизода"""
        episode = await media_crud.get_episode_with_details(
            db, episode_id=episode_id
        )
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Эпизод не найден.",
            )

        for field, value in episode_in.items():
            setattr(episode, field, value)

        try:
            await db.commit()
            await db.refresh(episode)
            logger.info(f"Эпизод id={episode_id} обновлён")
        except Exception as e:
            await db.rollback()
            logger.exception(
                f"Ошибка при обновлении эпизода id={episode_id}: {e}"
            )
            raise
        return episode

    async def delete_episode(
        self, db: AsyncSession, episode_id: int
    ) -> None:
        """Удаление эпизода"""
        episode = await media_crud.get_episode_with_details(
            db, episode_id=episode_id
        )
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Эпизод не найден.",
            )

        try:
            await db.delete(episode)
            await db.commit()
            logger.info(f"Эпизод id={episode_id} удалён")
        except Exception as e:
            await db.rollback()
            logger.exception(
                f"Ошибка при удалении эпизода id={episode_id}: {e}"
            )
            raise


media_service = MediaService()
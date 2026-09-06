# src/services/media.py
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.crud.media_crud import media_crud
from src.crud.crud_category import category_crud
from src.schemas.media import MediaCreate, MediaUpdate, EpisodeCreate, SeasonCreate
from src.model.model import Media, Category, Season, Episode


class MediaService:

    # ==================== MEDIA METHODS ====================

    async def create_media(self, db: AsyncSession, media_in: MediaCreate) -> Media:
        """
        Бизнес-логика создания медиа.
        Проверяет существование категорий и привязывает их через Many-to-Many.
        """
        # 1. Извлекаем ID категорий, если они переданы
        category_ids = media_in.category_ids or []

        # Удаляем category_ids из данных для создания самой модели Media
        media_data = media_in.model_dump(exclude={"category_ids"})

        # 2. Создаем объект Media
        db_obj = Media(**media_data)

        # 3. Если переданы категории, проверяем их существование и привязываем
        if category_ids:
            result = await db.execute(
                select(Category).where(Category.id.in_(category_ids))
            )
            categories = result.scalars().all()

            if len(categories) != len(category_ids):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Одна или несколько указанных категорий не найдены."
                )

            db_obj.categories = list(categories)

        # 4. Сохраняем в базу данных
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_media_by_id(self, db: AsyncSession, media_id: int) -> Media:
        """Получение базовой информации о медиа (без вложенных связей)."""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )
        return media

    async def get_media_with_relations(self, db: AsyncSession, media_id: int) -> Media:
        """Получение медиа со всей структурой."""
        media = await media_crud.get_full_details(db, media_id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )
        return media

    async def get_all_movies(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Получить список только фильмов"""
        return await media_crud.get_movies(db, skip=skip, limit=limit)

    async def get_all_tv_shows(self, db: AsyncSession, skip: int = 0, limit: int = 100):
        """Получить список только сериалов"""
        return await media_crud.get_tv_shows(db, skip=skip, limit=limit)

    async def get_media_by_category_id(self, db: AsyncSession, category_id: int):
        """Получить список медиа по конкретной категории"""
        category = await category_crud.get(db, id=category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена."
            )
        return await media_crud.get_by_category(db, category_id=category_id)

    async def search_media(self, db: AsyncSession, query: str, skip: int = 0, limit: int = 100):
        """Поиск медиа по названию или описанию"""
        if not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Поисковый запрос не может быть пустым."
            )
        return await media_crud.search(db, query=query, skip=skip, limit=limit)

    async def get_recent_media(self, db: AsyncSession, limit: int = 10):
        """Получить последние добавленные медиа"""
        return await media_crud.get_recent(db, limit=limit)

    async def update_media(self, db: AsyncSession, media_id: int, media_in: MediaUpdate) -> Media:
        """Обновление информации о медиа"""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )

        update_data = media_in.model_dump(exclude_unset=True)

        # Если обновляются категории
        if "category_ids" in update_data:
            category_ids = update_data.pop("category_ids")
            if category_ids is not None:
                await media_crud.update_categories(db, media_id, category_ids)

        # Обновляем остальные поля
        if update_data:
            for field, value in update_data.items():
                setattr(media, field, value)
            await db.commit()
            await db.refresh(media)

        return media

    async def delete_media(self, db: AsyncSession, media_id: int) -> None:
        """Удаление медиа"""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )

        await media_crud.remove(db, id=media_id)

    # ==================== SEASON METHODS ====================

    async def create_season(self, db: AsyncSession, season_in: SeasonCreate) -> Season:
        """Создание сезона с проверкой существования медиа"""
        # Проверяем существование медиа
        media = await media_crud.get(db, id=season_in.media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )

        # Проверяем, что медиа является сериалом
        if media.type != "tv_show":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сезоны можно добавлять только к сериалам."
            )

        # Проверяем, нет ли уже сезона с таким номером
        existing_season = await media_crud.get_season_by_number(
            db,
            media_id=season_in.media_id,
            season_number=season_in.season_number
        )
        if existing_season:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Сезон с номером {season_in.season_number} уже существует."
            )

        # Создаем сезон
        db_obj = Season(**season_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_seasons_by_media(self, db: AsyncSession, media_id: int) -> List[Season]:
        """Получить все сезоны сериала"""
        media = await media_crud.get(db, id=media_id)
        if not media:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Медиаресурс не найден."
            )

        return await media_crud.get_seasons_by_media(db, media_id=media_id)

    async def get_season_with_episodes(self, db: AsyncSession, season_id: int) -> Season:
        """Получить сезон со всеми эпизодами"""
        season = await media_crud.get_season_with_episodes(db, season_id=season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден."
            )
        return season

    async def update_season(self, db: AsyncSession, season_id: int, season_in: dict) -> Season:
        """Обновление сезона"""
        season = await media_crud.get_season_with_episodes(db, season_id=season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден."
            )

        for field, value in season_in.items():
            setattr(season, field, value)

        await db.commit()
        await db.refresh(season)
        return season

    async def delete_season(self, db: AsyncSession, season_id: int) -> None:
        """Удаление сезона"""
        season = await media_crud.get_season_with_episodes(db, season_id=season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден."
            )

        await db.delete(season)
        await db.commit()

    # ==================== EPISODE METHODS ====================

    async def create_episode(self, db: AsyncSession, episode_in: EpisodeCreate) -> Episode:
        """Создание эпизода с проверкой связей"""
        # Проверяем, что указан хотя бы один родитель (сезон или медиа)
        if episode_in.season_id is None and episode_in.media_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Эпизод должен быть привязан к сезону или медиа."
            )

        # Если указан сезон, проверяем его существование
        if episode_in.season_id:
            season = await media_crud.get_season_with_episodes(db, season_id=episode_in.season_id)
            if not season:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Сезон не найден."
                )

        # Если указано медиа, проверяем его существование
        if episode_in.media_id:
            media = await media_crud.get(db, id=episode_in.media_id)
            if not media:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Медиаресурс не найден."
                )

            # Если это сериал, эпизод должен быть привязан к сезону
            if media.type == "tv_show" and not episode_in.season_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Эпизоды сериала должны быть привязаны к сезону."
                )

        # Создаем эпизод
        db_obj = Episode(**episode_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_episodes_by_season(self, db: AsyncSession, season_id: int) -> List[Episode]:
        """Получить все эпизоды сезона"""
        season = await media_crud.get_season_with_episodes(db, season_id=season_id)
        if not season:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сезон не найден."
            )

        return await media_crud.get_episodes_by_season(db, season_id=season_id)

    async def get_episode_with_details(self, db: AsyncSession, episode_id: int) -> Episode:
        """Получить эпизод с информацией о родителях"""
        episode = await media_crud.get_episode_with_details(db, episode_id=episode_id)
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Эпизод не найден."
            )
        return episode

    async def update_episode(self, db: AsyncSession, episode_id: int, episode_in: dict) -> Episode:
        """Обновление эпизода"""
        episode = await media_crud.get_episode_with_details(db, episode_id=episode_id)
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Эпизод не найден."
            )

        for field, value in episode_in.items():
            setattr(episode, field, value)

        await db.commit()
        await db.refresh(episode)
        return episode

    async def delete_episode(self, db: AsyncSession, episode_id: int) -> None:
        """Удаление эпизода"""
        episode = await media_crud.get_episode_with_details(db, episode_id=episode_id)
        if not episode:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Эпизод не найден."
            )

        await db.delete(episode)
        await db.commit()




media_service = MediaService()
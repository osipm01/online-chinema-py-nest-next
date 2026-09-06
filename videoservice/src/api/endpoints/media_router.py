# src/api/v1/endpoints/media.py
from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_async_db
from src.services.media_service import media_service
from src.schemas.media import (
    MediaCreate,
    MediaRead,
    MediaDetailRead,
    MediaUpdate,
    EpisodeCreate,
    EpisodeRead,
    EpisodeUpdate,
    SeasonCreate,
    SeasonRead,
    SeasonWithEpisodesRead,
    SeasonUpdate,
    CategoryCreate,
    CategoryRead,
    CategoryWithMediaRead
)

router = APIRouter(prefix="/media", tags=["Media"])


# ==================== MEDIA ENDPOINTS ====================

@router.post("/create", response_model=MediaRead, status_code=status.HTTP_201_CREATED)
async def create_new_media(
    media_in: MediaCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Создание нового медиаресурса (фильма или сериала).
    Можно сразу передать список `category_ids` для привязки категорий.
    """
    return await media_service.create_media(db=db, media_in=media_in)


@router.get("/movies", response_model=List[MediaRead], status_code=status.HTTP_200_OK)
async def get_all_movies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """Получение списка всех фильмов с пагинацией"""
    return await media_service.get_all_movies(db=db, skip=skip, limit=limit)


@router.get("/tv-shows", response_model=List[MediaRead], status_code=status.HTTP_200_OK)
async def get_all_tv_shows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """Получение списка всех сериалов с пагинацией"""
    return await media_service.get_all_tv_shows(db=db, skip=skip, limit=limit)


@router.get("/category/{category_id}", response_model=List[MediaRead], status_code=status.HTTP_200_OK)
async def get_media_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Получение всех медиафайлов, привязанных к конкретной категории"""
    return await media_service.get_media_by_category_id(db=db, category_id=category_id)


@router.get("/search", response_model=List[MediaRead], status_code=status.HTTP_200_OK)
async def search_media(
    query: str = Query(..., min_length=1, description="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db)
):
    """Поиск медиа по названию или описанию"""
    return await media_service.search_media(db=db, query=query, skip=skip, limit=limit)


@router.get("/recent", response_model=List[MediaRead], status_code=status.HTTP_200_OK)
async def get_recent_media(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_async_db)
):
    """Получение последних добавленных медиа"""
    return await media_service.get_recent_media(db=db, limit=limit)


@router.get("/{media_id}", response_model=MediaDetailRead, status_code=status.HTTP_200_OK)
async def get_media_by_id(
    media_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Получение детальной информации о медиа по ID.
    Для фильма вернутся привязанные серии, для сериала — сезоны с сериями внутри.
    """
    return await media_service.get_media_with_relations(db=db, media_id=media_id)


@router.put("/{media_id}", response_model=MediaRead, status_code=status.HTTP_200_OK)
async def update_media(
    media_id: int,
    media_in: MediaUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Обновление информации о медиаресурсе"""
    return await media_service.update_media(db=db, media_id=media_id, media_in=media_in)


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Удаление медиаресурса"""
    await media_service.delete_media(db=db, media_id=media_id)


# ==================== SEASON ENDPOINTS ====================

@router.post("/seasons/create", response_model=SeasonRead, status_code=status.HTTP_201_CREATED)
async def create_season(
    season_in: SeasonCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Создание нового сезона для сериала"""
    return await media_service.create_season(db=db, season_in=season_in)


@router.get("/seasons/{season_id}", response_model=SeasonWithEpisodesRead, status_code=status.HTTP_200_OK)
async def get_season(
    season_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Получение сезона со всеми эпизодами"""
    return await media_service.get_season_with_episodes(db=db, season_id=season_id)


@router.get("/{media_id}/seasons", response_model=List[SeasonRead], status_code=status.HTTP_200_OK)
async def get_seasons_by_media(
    media_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Получение всех сезонов сериала"""
    return await media_service.get_seasons_by_media(db=db, media_id=media_id)


@router.put("/seasons/{season_id}", response_model=SeasonRead, status_code=status.HTTP_200_OK)
async def update_season(
    season_id: int,
    season_in: SeasonUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Обновление информации о сезоне"""
    update_data = season_in.model_dump(exclude_unset=True)
    return await media_service.update_season(db=db, season_id=season_id, season_in=update_data)


@router.delete("/seasons/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_season(
    season_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Удаление сезона"""
    await media_service.delete_season(db=db, season_id=season_id)


# ==================== EPISODE ENDPOINTS ====================

@router.post("/episodes/create", response_model=EpisodeRead, status_code=status.HTTP_201_CREATED)
async def create_episode(
    episode_in: EpisodeCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Создание нового эпизода"""
    return await media_service.create_episode(db=db, episode_in=episode_in)


@router.get("/episodes/{episode_id}", response_model=EpisodeRead, status_code=status.HTTP_200_OK)
async def get_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Получение эпизода с информацией о родителях"""
    return await media_service.get_episode_with_details(db=db, episode_id=episode_id)


@router.get("/seasons/{season_id}/episodes", response_model=List[EpisodeRead], status_code=status.HTTP_200_OK)
async def get_episodes_by_season(
    season_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Получение всех эпизодов сезона"""
    return await media_service.get_episodes_by_season(db=db, season_id=season_id)


@router.put("/episodes/{episode_id}", response_model=EpisodeRead, status_code=status.HTTP_200_OK)
async def update_episode(
    episode_id: int,
    episode_in: EpisodeUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Обновление информации об эпизоде"""
    update_data = episode_in.model_dump(exclude_unset=True)
    return await media_service.update_episode(db=db, episode_id=episode_id, episode_in=update_data)


@router.delete("/episodes/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_episode(
    episode_id: int,
    db: AsyncSession = Depends(get_async_db)
):
    """Удаление эпизода"""
    await media_service.delete_episode(db=db, episode_id=episode_id)


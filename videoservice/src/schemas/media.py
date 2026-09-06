# schemas/media.py

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, HttpUrl, Field
from enum import Enum


# Дублируем ваш Enum для валидации в Pydantic
class MediaTypeEnum(str, Enum):
    movie = "movie"
    tv_show = "tv_show"


# ==================== EPISODE SCHEMAS ====================

# Базовые поля
class EpisodeBase(BaseModel):
    title: str
    duration: int  # В секундах
    hls_link: str  # Можно использовать HttpUrl, если нужна строгая валидация URL


# Схема для создания
class EpisodeCreate(EpisodeBase):
    season_id: Optional[int] = None
    media_id: Optional[int] = None


# Схема для обновления
class EpisodeUpdate(BaseModel):
    title: Optional[str] = None
    duration: Optional[int] = None
    hls_link: Optional[str] = None
    season_id: Optional[int] = None
    media_id: Optional[int] = None


# Схема для чтения
class EpisodeRead(EpisodeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    season_id: Optional[int]
    media_id: Optional[int]


# ==================== SEASON SCHEMAS ====================

# Базовые поля
class SeasonBase(BaseModel):
    season_number: int
    title: str
    description: Optional[str] = None


# Схема для создания
class SeasonCreate(SeasonBase):
    media_id: int


# Схема для обновления
class SeasonUpdate(BaseModel):
    season_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


# Схема для чтения (базовая, без вложенных серий)
class SeasonRead(SeasonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    media_id: int


# Схема для чтения (полная, со списком серий)
class SeasonWithEpisodesRead(SeasonRead):
    episodes: List[EpisodeRead] = []


# ==================== MEDIA SCHEMAS ====================

# Базовые поля
class MediaBase(BaseModel):
    title: str
    description: str
    type: MediaTypeEnum


# Схема для создания
class MediaCreate(MediaBase):
    category_ids: Optional[List[int]] = None  # Для привязки категорий при создании


# Схема для обновления
class MediaUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[MediaTypeEnum] = None
    category_ids: Optional[List[int]] = None  # Для обновления категорий


# Схема для чтения (базовая, без вложенных связей)
class MediaRead(MediaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# Схема для детального отображения (включает сезоны ИЛИ эпизоды в зависимости от типа)
class MediaDetailRead(MediaRead):
    categories: List["CategoryRead"] = []
    seasons: List[SeasonWithEpisodesRead] = []
    episodes: List[EpisodeRead] = []  # Будет заполнено, если это фильм


# ==================== CATEGORY SCHEMAS ====================

class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CategoryWithMediaRead(CategoryRead):
    media: List[MediaRead] = []


# Обновляем ссылку после определения CategoryRead
MediaDetailRead.model_rebuild()
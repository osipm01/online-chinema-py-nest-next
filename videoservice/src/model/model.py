# todo
# разнести на файлы
from datetime import datetime
from enum import Enum as PyEnum
from time import timezone
from typing import List, Optional
from sqlalchemy import ForeignKey, String, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PG_ENUM

class Base(DeclarativeBase):
    pass

class MediaType(PyEnum):
    MOVIE = "movie"
    TV_SHOW = "tv_show"

media_category_association = Table(
    "media_category",
    Base.metadata,
    Column("media_id", ForeignKey("media.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Связь с медиа
    media: Mapped[List["Media"]] = relationship(
        secondary=media_category_association, back_populates="categories"
    )

class Media(Base):
    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))
    type: Mapped[MediaType] = mapped_column(
        String(50)
    )  # Хранит ENUM (movie или tv_show)

    # Связи
    categories: Mapped[List[Category]] = relationship(
        secondary=media_category_association, back_populates="media"
    )
    seasons: Mapped[List["Season"]] = relationship(
        back_populates="media", cascade="all, delete-orphan"
    )
    # Прямая связь с эпизодом только для фильмов
    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="media", cascade="all, delete-orphan"
    )

class Season(Base):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(primary_key=True)
    season_number: Mapped[int] = mapped_column()
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000))

    # Внешний ключ на Media
    media_id: Mapped[int] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"))
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Связи
    media: Mapped[Media] = relationship(back_populates="seasons")
    episodes: Mapped[List["Episode"]] = relationship(
        back_populates="season", cascade="all, delete-orphan"
    )

class Episode(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    duration: Mapped[int] = mapped_column()  # В секундах
    hls_link: Mapped[str] = mapped_column(String(500))  # Ссылка на .m3u8

    # Опциональный внешний ключ на Season (нужен только если это серия сериала)
    season_id: Mapped[Optional[int]] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    poster_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Опциональный внешний ключ на Media (нужен только если это одиночный фильм)
    media_id: Mapped[Optional[int]] = mapped_column(ForeignKey("media.id", ondelete="CASCADE"))

    # Связи
    season: Mapped[Optional[Season]] = relationship(back_populates="episodes")
    media: Mapped[Optional[Media]] = relationship(back_populates="episodes")

# модель User только для админки
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(String(255))  # Добавлено поле пароля
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
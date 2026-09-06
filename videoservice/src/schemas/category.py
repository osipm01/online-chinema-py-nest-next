# src/schemas/category.py
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


# Базовая схема
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название категории")


# Что нужно для создания категории
class CategoryCreate(CategoryBase):
    pass


# Что нужно для обновления категории
class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Новое название категории")


# Что возвращаем клиенту (с id)
class CategoryRead(CategoryBase):
    id: int

    # Включаем поддержку ORM-моделей SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


# Категория с количеством медиа (для списков)
class CategoryWithMediaCount(CategoryRead):
    media_count: int = 0


# Расширенная схема: категория со списком медиа
class CategoryWithMediaRead(CategoryRead):
    media: List["MediaRead"] = []


# Импорт для типизации (в конце файла для избежания циклических импортов)
from src.schemas.media import MediaRead

# Перестраиваем модель после импорта
CategoryWithMediaRead.model_rebuild()
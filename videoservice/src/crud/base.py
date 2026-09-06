# src/crud/base.py
from typing import Generic, Type, TypeVar, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

# Создаем переменные типов (плацехолдеры)
ModelType = TypeVar("ModelType")        # Для модели SQLAlchemy (например, Category)
CreateSchemaType = TypeVar("CreateSchemaType")  # Для Pydantic-схемы (например, CategoryCreate)

class CRUDBase(Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        При инициализации передаем конкретную модель класса.
        Например: CRUDBase(Category)
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """Поиск одной записи по ID"""
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Получение списка записей с пагинацией"""
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        """Создание новой записи"""
        # Превращаем Pydantic-схему в словарь и распаковываем в модель SQLAlchemy
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()       # Сохраняем в БД
        await db.refresh(db_obj) # Обновляем объект, чтобы у него появился id из БД
        return db_obj

    async def remove(self, db: AsyncSession, id: int) -> None:
        """Удаление записи по ID"""
        await db.execute(delete(self.model).where(self.model.id == id))
        await db.commit()

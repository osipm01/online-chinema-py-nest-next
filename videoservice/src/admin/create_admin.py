# create_admin.py
import asyncio
from sqlalchemy import select
from src.core.database import AsyncSessionLocal
from src.model.model import User


async def create_admin():
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли уже администратор
        stmt = select(User).where(User.username == "admin")
        result = await session.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            print(f"Администратор уже существует: {existing_user.username}")
            return

        # Создаем нового администратора с паролем
        admin_user = User(
            username="admin",
            email="admin@example.com",
            password="admin_password_123",  # Временный пароль для разработки
            is_active=True
        )

        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)
        print(f"Администратор успешно создан! ID: {admin_user.id}")
        print("Логин: admin")
        print("Пароль: admin_password_123")



asyncio.run(create_admin())
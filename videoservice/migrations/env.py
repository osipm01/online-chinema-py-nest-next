import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from src.model.model import Base

# Это объект конфигурации Alembic.
config = context.config

# Настройка логирования.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Сюда добавьте импорт Base.metadata вашего приложения для работы autogenerate
# (например: from app.db import Base; target_metadata = Base.metadata)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в режиме 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Вспомогательная функция для выполнения миграций внутри синхронного контекста."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Асинхронное создание движка и подключение."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # run_sync выполняет синхронную функцию do_run_migrations в асинхронной среде
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в режиме 'online'."""
    # Запускаем асинхронный цикл для выполнения миграций
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()

else:
    run_migrations_online()

from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin, ModelView
from starlette_admin.auth import AuthProvider
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from sqlalchemy import select

# Импортируйте ваши компоненты базы данных и модели
from src.core.database import AsyncSessionLocal, engine
from src.model.model import Base, User  # Base нужен для автоподтягивания


# --- 1. Провайдер Аутентификации ---
class SimpleAdminAuthProvider(AuthProvider):
    async def login(
        self,
        username: str,
        password: str,
        remember_me: bool,
        request: Request
    ) -> Response:
        async with AsyncSessionLocal() as session:
            # Ищем активного пользователя
            stmt = select(User).where(User.username == username, User.is_active == True)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            # ВНИМАНИЕ: На этапе разработки проверяем сырой пароль "admin_password_123"
            if user and password == "admin_password_123":
                # Записываем данные в сессию Starlette-Admin
                request.session.update({"user": {"id": user.id, "username": user.username}})
                return RedirectResponse(url=request.query_params.get("next", "/admin"), status_code=303)

        # Если данные неверны, возвращаем обратно на страницу логина с ошибкой
        return RedirectResponse(url=f"{request.url_for('admin:login')}?error=Invalid+credentials", status_code=303)

    async def logout(self, request: Request) -> RedirectResponse:
        request.session.clear()
        return RedirectResponse(url=request.url_for("admin:index"), status_code=303)

    async def is_authenticated(self, request: Request) -> bool:
        # Если юзер есть в сессии — у него полный доступ
        return "user" in request.session


# --- 2. Функция инициализации админки ---
def setup_admin(app: FastAPI) -> None:
    # Создаем объект админки (обратите внимание на secret_key)
    admin = Admin(
        engine,
        title="Панель управления",
        base_url="/admin",
        auth_provider=SimpleAdminAuthProvider(),
        secret_key="change-me"  # Добавьте секретный ключ для сессий
    )

    # --- 3. Автоматическое подтягивание всех моделей ---
    for model_name, table_obj in Base.metadata.tables.items():
        # Системную таблицу миграций Alembic пропускаем, она в админке не нужна
        if model_name == "alembic_version":
            continue

        # Получаем сам класс SQLAlchemy по имени таблицы
        model_class = None
        for mapper in Base.registry.mappers:
            if getattr(mapper.class_, "__tablename__", None) == model_name:
                model_class = mapper.class_
                break

        if model_class:
            # Создаем динамический View для модели
            class AutoModelView(ModelView):
                # Настройки отображения
                page_size = 25
                page_size_options = [25, 50, 100]
                # Можно указать иконку для модели
                icon = "fa fa-table"

            # Регистрируем модель в админке
            admin.add_view(AutoModelView(model_class))

    # Монтируем админку в приложение FastAPI
    admin.mount_to(app)
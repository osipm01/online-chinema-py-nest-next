from datetime import timedelta
from typing import Optional

from django.contrib.auth.hashers import check_password
from django.utils import timezone
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from .models import User
from .core.JWTService import jwt_service, RolseEnum, TokenType


class AuthService:
    """Сервис авторизации и CRUD пользователей."""

    # ---------- helpers ----------
    @staticmethod
    def _role_to_enum(role_str: str) -> RolseEnum:
        try:
            return RolseEnum[role_str.upper()]
        except KeyError:
            raise ValueError(f"Неизвестная роль: {role_str}")

    # ---------- CRUD ----------
    @staticmethod
    def create_user(username: str, password: str, role: str = "user") -> User:
        role_enum = AuthService._role_to_enum(role)
        user = User.objects.create_user(
            username=username,
            password=password,
            role=role_enum.name.lower(),
        )
        return user

    @staticmethod
    def get_user(user_id: int) -> Optional[User]:
        return User.objects.filter(id=user_id).first()

    @staticmethod
    def list_users():
        return User.objects.all().order_by("id")

    @staticmethod
    def update_user(user: User, **fields) -> User:
        if "username" in fields and fields["username"]:
            user.username = fields["username"]
        if "role" in fields and fields["role"]:
            role_enum = AuthService._role_to_enum(fields["role"])
            user.role = role_enum.name.lower()
        user.save()
        return user

    @staticmethod
    def delete_user(user: User) -> None:
        user.delete()

    # ---------- auth ----------
    @staticmethod
    def authenticate(username: str, password: str) -> User:
        user = User.objects.filter(username=username).first()
        if not user or not check_password(password, user.password):
            raise ValueError("Неверный логин или пароль")
        if not user.is_active:
            raise ValueError("Пользователь заблокирован")
        return user

    @staticmethod
    def login(username: str, password: str) -> dict:
        user = AuthService.authenticate(username, password)
        role_enum = AuthService._role_to_enum(user.role)
        tokens = jwt_service.generate_token_pair(user.id, role_enum)

        # Сохраняем токены в БД (если нужно для blacklist / logout)
        user.access_token = tokens["access_token"]
        user.refresh_token = tokens["refresh_token"]
        user.save(update_fields=["access_token", "refresh_token"])

        return {"user": user, **tokens}

    @staticmethod
    def refresh(refresh_token: str) -> dict:
        try:
            payload = jwt_service.validate_refresh_token(refresh_token)
        except ValueError as e:
            raise ValueError(str(e))

        user_id = int(payload["sub"])
        user = User.objects.filter(id=user_id).first()
        if not user or not user.is_active:
            raise ValueError("Пользователь не найден или заблокирован")

        # Проверка, что refresh-токен не отозван
        if user.refresh_token and user.refresh_token != refresh_token:
            raise ValueError("Refresh-токен отозван")

        role_enum = AuthService._role_to_enum(user.role)
        tokens = jwt_service.generate_token_pair(user.id, role_enum)

        user.access_token = tokens["access_token"]
        user.refresh_token = tokens["refresh_token"]
        user.save(update_fields=["access_token", "refresh_token"])
        return tokens

    @staticmethod
    def logout(user: User) -> None:
        user.access_token = None
        user.refresh_token = None
        user.save(update_fields=["access_token", "refresh_token"])

    # ---------- password ----------
    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not check_password(old_password, user.password):
            raise ValueError("Старый пароль неверен")
        user.set_password(new_password)
        user.access_token = None
        user.refresh_token = None
        user.save()

    @staticmethod
    def create_password_reset_token(user: User) -> str:
        """Генерирует короткоживущий токен для сброса пароля."""
        payload = {
            "sub": str(user.id),
            "type": "password_reset",
            "iat": timezone.now(),
            "exp": timezone.now() + timedelta(minutes=15),
        }
        return jwt.encode(payload, jwt_service.secret, algorithm=jwt_service.aloghoritm)

    @staticmethod
    def reset_password(token: str, new_password: str) -> User:
        try:
            payload = jwt.decode(
                token,
                jwt_service.secret,
                algorithms=[jwt_service.aloghoritm],
            )
        except ExpiredSignatureError:
            raise ValueError("Срок действия токена истёк")
        except InvalidTokenError as e:
            raise ValueError(f"Недействительный токен: {e}")

        if payload.get("type") != "password_reset":
            raise ValueError("Неверный тип токена")

        user = User.objects.filter(id=int(payload["sub"])).first()
        if not user:
            raise ValueError("Пользователь не найден")

        user.set_password(new_password)
        user.access_token = None
        user.refresh_token = None
        user.save()
        return user


    @staticmethod
    def update_user(user: User, **fields) -> User:
        if "username" in fields and fields["username"]:
            user.username = fields["username"]
            if "role" in fields and fields["role"]:
                role_enum = AuthService._role_to_enum(fields["role"])
                user.role = role_enum.name.lower()
                if "is_active" in fields and fields["is_active"] is not None:
                    user.is_active = fields["is_active"]
                    if "password" in fields and fields["password"]:
                        user.set_password(fields["password"])
                        # при смене пароля админом — сбрасываем токены пользователя
                        user.access_token = None
                        user.refresh_token = None
                        user.save()
                        return user

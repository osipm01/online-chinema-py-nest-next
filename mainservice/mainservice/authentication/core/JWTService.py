from enum import Enum
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError

from .settings import settings


# Роли в бд и payload
# "admin"
# "user"
# "meneger"
class RolseEnum(Enum):
    ADMIN = 1
    USER = 2
    MENEGER = 3


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class JWGService:

    # конфиг
    def __init__(self) -> None:
        self.secret = settings.JWT_SECRET  # jwt секрет
        self.aloghoritm = settings.ALGHORITM  # алгоритм
        self.token_timer = settings.REFRESH_TOKEN_TIMER  # токен refresh - действует 72 часа
        self.access_token_timer = getattr(settings, "ACCESS_TOKEN_TIMER", 15)  # минуты (по умолчанию 15)

    def _generate_token(
        self,
        user_id: int,
        role: RolseEnum,
        token_type: TokenType,
        expires_delta: timedelta,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Внутренний метод генерации токена."""
        now = datetime.utcnow()
        payload: Dict[str, Any] = {
            "sub": str(user_id),
            "role": role.name,
            "type": token_type.value,
            "iat": now,
            "exp": now + expires_delta,
        }
        if extra_claims:
            payload.update(extra_claims)

        return jwt.encode(payload, self.secret, algorithm=self.aloghoritm)

    def generate_access_token(
        self,
        user_id: int,
        role: RolseEnum,
        expires_minutes: Optional[int] = None,
    ) -> str:
        """Генерация access токена."""
        minutes = expires_minutes if expires_minutes is not None else self.access_token_timer
        return self._generate_token(
            user_id=user_id,
            role=role,
            token_type=TokenType.ACCESS,
            expires_delta=timedelta(minutes=minutes),
        )

    def generate_refresh_token(
        self,
        user_id: int,
        role: RolseEnum,
        expires_hours: Optional[int] = None,
    ) -> str:
        """Генерация refresh токена."""
        hours = expires_hours if expires_hours is not None else self.token_timer
        return self._generate_token(
            user_id=user_id,
            role=role,
            token_type=TokenType.REFRESH,
            expires_delta=timedelta(hours=hours),
        )

    def generate_token_pair(
        self,
        user_id: int,
        role: RolseEnum,
    ) -> Dict[str, str]:
        """Генерация пары access + refresh токенов."""
        return {
            "access_token": self.generate_access_token(user_id, role),
            "refresh_token": self.generate_refresh_token(user_id, role),
            "token_type": "Bearer",
        }

    def _decode_token(
        self,
        token: str,
        expected_type: Optional[TokenType] = None,
    ) -> Dict[str, Any]:
        """Внутренний метод декодирования и валидации токена."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.aloghoritm],
            )
        except ExpiredSignatureError:
            raise ValueError("Token expired")
        except InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")

        if expected_type is not None and payload.get("type") != expected_type.value:
            raise ValueError(
                f"Invalid token type: expected {expected_type.value}, "
                f"got {payload.get('type')}"
            )

        return payload

    def validate_access_token(self, token: str) -> Dict[str, Any]:
        """Валидация access токена."""
        return self._decode_token(token, expected_type=TokenType.ACCESS)

    def validate_refresh_token(self, token: str) -> Dict[str, Any]:
        """Валидация refresh токена."""
        return self._decode_token(token, expected_type=TokenType.REFRESH)

    def refresh_access_token(
        self,
        refresh_token: str,
    ) -> Dict[str, str]:
        """Обновление access токена по refresh токену."""
        payload = self.validate_refresh_token(refresh_token)

        try:
            role = RolseEnum[payload["role"]]
        except KeyError:
            raise ValueError(f"Unknown role: {payload.get('role')}")

        user_id = int(payload["sub"])
        return self.generate_token_pair(user_id, role)

    @staticmethod
    def get_user_id(payload: Dict[str, Any]) -> int:
        """Извлечь user_id из payload."""
        return int(payload["sub"])

    @staticmethod
    def get_role(payload: Dict[str, Any]) -> RolseEnum:
        """Извлечь роль из payload."""
        return RolseEnum[payload["role"]]


jwt_service = JWGService()

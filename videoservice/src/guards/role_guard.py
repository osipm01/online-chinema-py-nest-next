from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from src.core.database import settings

ALGORITHM = "HS256"

# Автоматически ищет заголовок "Authorization: Bearer <токен>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_role(token: str = Depends(oauth2_scheme)) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось валидировать учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Декодируем JWT
        payload = jwt.decode(token, settings.SECRET_JWT_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")

        # Если роли внутри токена нет, токен невалиден для этого сервера
        if role is None:
            raise credentials_exception

        return role

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception


# Функция-фабрика для проверки ролей
def role_guard(allowed_roles: List[str]):
    async def role_dependency(user_role: str = Depends(get_current_role)):
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен: недостаточно прав"
            )
        return user_role

    return role_dependency


# # Пример использования в эндпоинтах
# @app.get("/secure-data")
# async def get_secure_data(role: str = Depends(verify_role(["admin", "manager"]))):
#     # Если выполнение дошло сюда, значит роль точно admin или manager
#     return {"message": "Доступ разрешен", "your_role": role}

from functools import wraps
from fastapi import FastAPI, Request, HTTPException, status

# Функция-декоратор проверка можно ли передать ссылки на контент пользователю
def require_token():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get("request")
            if not request:
                raise RuntimeError("Декоратор @require_token требует наличия 'request: Request' в аргументах эндпоинта")

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Отсутствует или неверен Bearer токен",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            token = auth_header.split(" ")[1]

            if token != "my_secret_token":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидный токен"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


#@require_token()


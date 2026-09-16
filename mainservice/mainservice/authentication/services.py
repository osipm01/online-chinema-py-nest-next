# services.py
"""
Бизнес-логика для работы с пользователями.
Слой сервисов: оркестрация, валидация сценариев, транзакции.
Все обращения к БД — только через selectors.py.
"""

from typing import Optional, Dict, Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from . import selectors

User = get_user_model()


# ============================================================
# РЕГИСТРАЦИЯ
# ============================================================

@transaction.atomic
def user_register(
    *,
    username: str,
    password: str,
    role: str = 'user',
    **extra_fields: Any,
) -> User:
    """
    Регистрация нового пользователя.
    По умолчанию роль — 'user', is_active=True, is_staff=False.
    """
    if not password:
        raise ValidationError('Пароль обязателен')

    user = selectors.user_create(
        username=username,
        password=password,
        role=role,
        **extra_fields,
    )
    return user


# ============================================================
# АУТЕНТИФИКАЦИЯ
# ============================================================

@transaction.atomic
def user_login(
    *,
    username: str,
    password: str,
    access_token: Optional[str] = None,
    refresh_token: Optional[str] = None,
) -> User:
    """
    Проверяет учётные данные и (опционально) сохраняет токены.
    Возвращает пользователя при успехе, кидает ValidationError при провале.
    """
    user = selectors.user_get_by_username(username=username)

    if not user:
        # не раскрываем, существует ли пользователь
        raise ValidationError('Неверное имя пользователя или пароль')

    if not user.is_active:
        raise ValidationError('Учётная запись отключена')

    if not selectors.user_check_password(user=user, raw_password=password):
        raise ValidationError('Неверное имя пользователя или пароль')

    if access_token or refresh_token:
        selectors.user_update_tokens(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    return user


@transaction.atomic
def user_logout(*, user: User) -> User:
    """Выход — очистка токенов."""
    return selectors.user_clear_tokens(user=user)


# ============================================================
# ПРОФИЛЬ
# ============================================================

@transaction.atomic
def user_update_profile(
    *,
    user: User,
    username: Optional[str] = None,
    role: Optional[str] = None,
    **extra_fields: Any,
) -> User:
    """
    Обновление профиля обычным пользователем (без права менять is_active/is_staff).
    """
    return selectors.user_update(
        user=user,
        username=username,
        role=role,
        **extra_fields,
    )


@transaction.atomic
def user_admin_update(
    *,
    user: User,
    username: Optional[str] = None,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_staff: Optional[bool] = None,
    **extra_fields: Any,
) -> User:
    """
    Обновление пользователя администратором — с правом менять служебные поля.
    """
    return selectors.user_update(
        user=user,
        username=username,
        role=role,
        is_active=is_active,
        is_staff=is_staff,
        **extra_fields,
    )


# ============================================================
# ПАРОЛЬ
# ============================================================

@transaction.atomic
def user_change_password(
    *,
    user: User,
    old_password: str,
    new_password: str,
) -> User:
    """
    Смена пароля с проверкой старого.
    При успехе — сбрасывает токены (нужно перелогиниться).
    """
    if not selectors.user_check_password(user=user, raw_password=old_password):
        raise ValidationError('Неверный текущий пароль')

    if not new_password or len(new_password) < 6:
        raise ValidationError('Новый пароль слишком короткий')

    if old_password == new_password:
        raise ValidationError('Новый пароль совпадает со старым')

    return selectors.user_change_password(
        user=user,
        new_password=new_password,
    )


@transaction.atomic
def user_reset_password(
    *,
    username: str,
    new_password: str,
) -> User:
    """
    Сброс пароля (например, администратором или после подтверждения по email).
    """
    if not new_password or len(new_password) < 6:
        raise ValidationError('Пароль слишком короткий')

    return selectors.user_reset_password(
        username=username,
        new_password=new_password,
    )


# ============================================================
# ТОКЕНЫ
# ============================================================

@transaction.atomic
def user_refresh_tokens(
    *,
    user: User,
    access_token: str,
    refresh_token: Optional[str] = None,
) -> User:
    """
    Обновление access-токена (и, опционально, refresh-токена).
    """
    if not access_token:
        raise ValidationError('access_token обязателен')

    return selectors.user_update_tokens(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


# ============================================================
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (АДМИН)
# ============================================================

@transaction.atomic
def user_block(*, user: User) -> User:
    """Блокировка пользователя (деактивация + сброс токенов)."""
    if not user.is_active:
        raise ValidationError('Пользователь уже заблокирован')
    return selectors.user_deactivate(user=user)


@transaction.atomic
def user_unblock(*, user: User) -> User:
    """Разблокировка пользователя."""
    if user.is_active:
        raise ValidationError('Пользователь уже активен')
    return selectors.user_update(user=user, is_active=True)


@transaction.atomic
def user_delete(*, user: User) -> None:
    """Полное удаление пользователя."""
    selectors.user_delete(user=user)


# ============================================================
# РОЛИ
# ============================================================

ALLOWED_ROLES = {'user', 'moderator', 'admin'}


@transaction.atomic
def user_set_role(*, user: User, role: str) -> User:
    """
    Смена роли с валидацией по списку допустимых.
    """
    if role not in ALLOWED_ROLES:
        raise ValidationError(f'Недопустимая роль: {role}')
    return selectors.user_update(user=user, role=role)

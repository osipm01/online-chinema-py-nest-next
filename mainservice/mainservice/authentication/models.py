from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Имя пользователя обязательно')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)  # Хеширует пароль автоматически
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    # Уникальное имя пользователя (логин)
    username = models.CharField(max_length=150, unique=True)

    # Роль пользователя (строка)
    role = models.CharField(max_length=50, default='user')

    # Дата создания (заполняется автоматически при создании)
    created_at = models.DateTimeField(default=timezone.now)

    # Токены доступа (обычно используются для JWT)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)

    # Служебные поля Django для админки
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # Поле для авторизации
    REQUIRED_FIELDS = []         # Дополнительные обязательные поля при создании superuser

    def __str__(self):
        return f"{self.username} ({self.role})"

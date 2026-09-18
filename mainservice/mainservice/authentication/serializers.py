from rest_framework import serializers

from .models import User
from .core.JWTService import RolseEnum


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения данных пользователя."""
    password = serializers.CharField(write_only=True, required=False, min_length=6)

    class Meta:
        model = User
        fields = (
            "id", "username", "role", "password",
            "created_at", "is_active", "is_staff",
        )
        read_only_fields = ("id", "created_at", "is_staff")


class RegisterSerializer(serializers.Serializer):
    """Регистрация нового пользователя."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(
        choices=[r.name.lower() for r in RolseEnum],
        default="user",
    )

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value


class LoginSerializer(serializers.Serializer):
    """Авторизация по username + password."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RefreshSerializer(serializers.Serializer):
    """Обновление токенов по refresh."""
    refresh_token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer):
    """Смена пароля авторизованным пользователем."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=6)


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Запрос на сброс пароля (получение reset-токена)."""
    username = serializers.CharField()


class ResetPasswordConfirmSerializer(serializers.Serializer):
    """Подтверждение сброса пароля по токену."""
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)


class UpdateUserSerializer(serializers.Serializer):
    """Редактирование профиля."""
    username = serializers.CharField(max_length=150, required=False)
    role = serializers.ChoiceField(
        choices=[r.name.lower() for r in RolseEnum],
        required=False,
    )

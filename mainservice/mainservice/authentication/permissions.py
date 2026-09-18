from rest_framework.permissions import BasePermission

from .core.JWTService import jwt_service, RolseEnum


class JWTAuthenticated(BasePermission):
    """
    Проверяет access-токен из заголовка Authorization: Bearer <token>.
    Кладёт payload в request.jwt_payload, а пользователя — в request.user_obj.
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return False

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = jwt_service.validate_access_token(token)
        except ValueError:
            return False

        request.jwt_payload = payload

        from .models import User
        try:
            user = User.objects.get(id=int(payload["sub"]))
        except (User.DoesNotExist, KeyError, ValueError):
            return False

        if not user.is_active:
            return False

        request.user_obj = user
        return True


class IsAdmin(BasePermission):
    """Только для роли admin."""
    def has_permission(self, request, view):
        return (
            getattr(request, "jwt_payload", {}).get("role") == RolseEnum.ADMIN.name
        )


class IsManagerOrAdmin(BasePermission):
    """Для роли meneger или admin."""
    def has_permission(self, request, view):
        role = getattr(request, "jwt_payload", {}).get("role")
        return role in (RolseEnum.ADMIN.name, RolseEnum.MENEGER.name)


class IsSelfOrAdmin(BasePermission):
    """Разрешить доступ к объекту самому пользователю или админу."""
    def has_object_permission(self, request, view, obj):
        if getattr(request, "jwt_payload", {}).get("role") == RolseEnum.ADMIN.name:
            return True
        return str(obj.id) == str(getattr(request, "jwt_payload", {}).get("sub"))

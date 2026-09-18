from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .permissions import JWTAuthenticated, IsAdmin
from .serializers import (
    RegisterSerializer, LoginSerializer, RefreshSerializer,
    ChangePasswordSerializer, ResetPasswordRequestSerializer,
    ResetPasswordConfirmSerializer, UpdateUserSerializer, UserSerializer,
)
from .services import AuthService



# ================= AUTH =================

class RegisterView(APIView):
    """POST /api/auth/register/ — регистрация пользователя."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = AuthService.create_user(
                username=data["username"],
                password=data["password"],
                role=data["role"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = AuthService.login(data["username"], data["password"])
        return Response(
            {
                "user": UserSerializer(user).data,
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": "Bearer",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """POST /api/auth/login/ — вход."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = AuthService.login(data["username"], data["password"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "user": UserSerializer(result["user"]).data,
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "token_type": "Bearer",
            }
        )


class RefreshTokenView(APIView):
    """POST /api/auth/refresh/ — обновление пары токенов."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            tokens = AuthService.refresh(serializer.validated_data["refresh_token"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(tokens)


class LogoutView(APIView):
    """POST /api/auth/logout/ — выход (отзыв токенов)."""
    permission_classes = [JWTAuthenticated]

    def post(self, request):
        AuthService.logout(request.user_obj)
        return Response({"detail": "Вы вышли из системы"})


class MeView(APIView):
    """GET /api/auth/me/ — проверка авторизации и данные о себе."""
    permission_classes = [JWTAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user_obj).data)


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — смена пароля."""
    permission_classes = [JWTAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            AuthService.change_password(
                request.user_obj, data["old_password"], data["new_password"]
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Пароль успешно изменён"})


class ResetPasswordRequestView(APIView):
    """POST /api/auth/reset-password/ — запрос токена для сброса."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]

        user = User.objects.filter(username=username).first()
        # Не раскрываем, существует ли пользователь — всегда 200
        if user:
            token = AuthService.create_password_reset_token(user)
            # В реальном проекте тут отправка email/SMS
            return Response({"detail": "Токен сброса создан", "reset_token": token})
        return Response({"detail": "Если пользователь существует, токен отправлен"})


class ResetPasswordConfirmView(APIView):
    """POST /api/auth/reset-password/confirm/ — установка нового пароля."""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            AuthService.reset_password(data["token"], data["new_password"])
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Пароль успешно сброшен"})


# ================= CRUD USERS =================

class UserListCreateView(APIView):
    """
    GET  /api/users/      — список (только admin)
    POST /api/users/      — создание (только admin)
    """
    permission_classes = [JWTAuthenticated, IsAdmin]

    def get(self, request):
        users = AuthService.list_users()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = AuthService.create_user(
                username=data["username"],
                password=data["password"],
                role=data["role"],
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailView(APIView):
    """
    GET    /api/users/<id>/   — просмотр (admin или сам пользователь)
    PATCH  /api/users/<id>/   — редактирование (admin)
    DELETE /api/users/<id>/   — удаление (admin)
    """
    permission_classes = [JWTAuthenticated]

    def _get_user(self, pk: int) -> User:
        user = AuthService.get_user(pk)
        if not user:
            raise User.DoesNotExist
        return user

    def _check_self_or_admin(self, request, user) -> bool:
        role = request.jwt_payload.get("role")
        is_admin = role == "ADMIN"
        is_self = str(user.id) == str(request.jwt_payload.get("sub"))
        return is_admin or is_self

    def get(self, request, pk: int):
        try:
            user = self._get_user(pk)
        except User.DoesNotExist:
            return Response({"detail": "Не найдено"}, status=404)
        if not self._check_self_or_admin(request, user):
            return Response({"detail": "Нет доступа"}, status=403)
        return Response(UserSerializer(user).data)

    def patch(self, request, pk: int):
        if request.jwt_payload.get("role") != "ADMIN":
            return Response({"detail": "Только admin"}, status=403)
        try:
            user = self._get_user(pk)
        except User.DoesNotExist:
            return Response({"detail": "Не найдено"}, status=404)

        serializer = UpdateUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = AuthService.update_user(user, **serializer.validated_data)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)
        return Response(UserSerializer(user).data)

    def delete(self, request, pk: int):
        if request.jwt_payload.get("role") != "ADMIN":
            return Response({"detail": "Только admin"}, status=403)
        try:
            user = self._get_user(pk)
        except User.DoesNotExist:
            return Response({"detail": "Не найдено"}, status=404)
        AuthService.delete_user(user)
        return Response(status=204)

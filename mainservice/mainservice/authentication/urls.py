# users/urls.py
from django.urls import path
from . import views

from .views import (
    RegisterView, LoginView, RefreshTokenView, LogoutView,
    MeView, ChangePasswordView,
    ResetPasswordRequestView, ResetPasswordConfirmView,
    UserListCreateView, UserDetailView,
)

app_name = 'authentication'

# authentication/urls.py
urlpatterns = [
    # auth
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/refresh/", RefreshTokenView.as_view()),
    path("auth/logout/", LogoutView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("auth/change-password/", ChangePasswordView.as_view()),
    path("auth/reset-password/", ResetPasswordRequestView.as_view()),
    path("auth/reset-password/confirm/", ResetPasswordConfirmView.as_view()),

    # users CRUD
    path("", UserListCreateView.as_view()),                 # GET/POST /api/users/
    path("<int:pk>/", UserDetailView.as_view()),            # GET/PUT/PATCH/DELETE /api/users/<pk>/
]

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Поля, которые будут отображаться в списке пользователей
    list_display = ('username', 'role', 'created_at', 'is_staff', 'is_active')

    # Фильтры в правой колонке
    list_filter = ('role', 'is_staff', 'is_active')

    # Настройки отображения полей на странице редактирования пользователя
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('role',)}),
        ('Токены', {'fields': ('access_token', 'refresh_token')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'created_at')}),
    )

    # Поля, которые нельзя редактировать вручную (дата создания заполняется автоматически)
    readonly_fields = ('created_at',)

    # Поля, по которым будет работать поиск
    search_fields = ('username', 'role')
    ordering = ('-created_at',)

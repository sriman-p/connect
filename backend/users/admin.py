from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    Customized for email-based authentication.
    """

    list_display = [
        'email',
        'full_name',
        'is_verified',
        'is_active',
        'is_staff',
        'created_at',
    ]
    list_filter = [
        'is_verified',
        'is_active',
        'is_staff',
        'is_superuser',
        'created_at',
    ]
    search_fields = ['email', 'full_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_login']

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('full_name', 'avatar_url', 'bio', 'timezone')
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_verified',
                'is_staff',
                'is_superuser',
                'global_permissions',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'full_name',
                'password1',
                'password2',
                'is_active',
                'is_verified',
                'is_staff',
            ),
        }),
    )

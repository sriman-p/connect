from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, PasskeyCredential, PasskeyAuthenticationAttempt, PasskeyRegistrationSession


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


@admin.register(PasskeyCredential)
class PasskeyCredentialAdmin(admin.ModelAdmin):
    """Admin interface for passkey credentials."""

    list_display = [
        'name', 'user', 'authenticator_type',
        'is_active', 'usage_count', 'last_used_at', 'created_at'
    ]
    list_filter = ['authenticator_type', 'is_active', 'is_backup_eligible', 'created_at']
    search_fields = ['name', 'user__email', 'device_name', 'credential_id']
    raw_id_fields = ['user']
    readonly_fields = [
        'credential_id', 'public_key', 'aaguid', 'sign_count',
        'usage_count', 'last_used_at', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'credential_id', 'public_key')
        }),
        ('Authenticator Details', {
            'fields': (
                'authenticator_type', 'aaguid', 'attestation_format',
                'attestation_data', 'transports'
            )
        }),
        ('Device Information', {
            'fields': ('device_name', 'user_agent', 'ip_address')
        }),
        ('Status & Usage', {
            'fields': (
                'is_active', 'is_backup_eligible', 'is_backup_state',
                'usage_count', 'last_used_at', 'sign_count'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PasskeyAuthenticationAttempt)
class PasskeyAuthenticationAttemptAdmin(admin.ModelAdmin):
    """Admin interface for passkey authentication attempts."""

    list_display = [
        'user', 'credential', 'status',
        'ip_address', 'country_code', 'attempted_at'
    ]
    list_filter = ['status', 'attempted_at']
    search_fields = ['user__email', 'ip_address', 'credential__name']
    raw_id_fields = ['user', 'credential']
    readonly_fields = ['attempted_at']
    date_hierarchy = 'attempted_at'

    fieldsets = (
        ('Attempt Details', {
            'fields': ('user', 'credential', 'status', 'challenge')
        }),
        ('Request Metadata', {
            'fields': ('user_agent', 'ip_address', 'country_code', 'city')
        }),
        ('Error Details', {
            'fields': ('error_message',)
        }),
        ('Timestamp', {
            'fields': ('attempted_at',)
        }),
    )


@admin.register(PasskeyRegistrationSession)
class PasskeyRegistrationSessionAdmin(admin.ModelAdmin):
    """Admin interface for passkey registration sessions."""

    list_display = [
        'user', 'is_completed', 'is_expired',
        'created_at', 'expires_at'
    ]
    list_filter = ['is_completed', 'is_expired', 'created_at']
    search_fields = ['user__email', 'challenge']
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Session Details', {
            'fields': ('user', 'challenge', 'is_completed', 'is_expired')
        }),
        ('Request Metadata', {
            'fields': ('user_agent', 'ip_address')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at', 'completed_at')
        }),
    )

"""
Integrations Admin Interface
"""

from django.contrib import admin
from .models import Integration, APIKey, Webhook, WebhookDelivery, IntegrationLog


@admin.register(Integration)
class IntegrationAdmin(admin.ModelAdmin):
    """Admin interface for integrations."""

    list_display = [
        'name', 'integration_type', 'workspace', 'is_active',
        'sync_status', 'last_synced_at', 'installed_at'
    ]
    list_filter = ['integration_type', 'is_active', 'sync_status', 'auto_sync']
    search_fields = ['name', 'workspace__name']
    readonly_fields = ['installed_at', 'updated_at', 'last_synced_at']
    date_hierarchy = 'installed_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'name', 'integration_type', 'installed_by')
        }),
        ('Configuration', {
            'fields': ('config', 'is_active')
        }),
        ('OAuth Tokens', {
            'fields': ('access_token', 'refresh_token', 'token_expires_at'),
            'classes': ('collapse',)
        }),
        ('Sync Settings', {
            'fields': ('auto_sync', 'sync_interval_minutes')
        }),
        ('Sync Status', {
            'fields': ('sync_status', 'sync_error', 'last_synced_at')
        }),
        ('Timestamps', {
            'fields': ('installed_at', 'updated_at')
        }),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    """Admin interface for API keys."""

    list_display = [
        'name', 'workspace', 'is_active', 'is_revoked',
        'rate_limit_per_hour', 'usage_count', 'last_used_at', 'created_at'
    ]
    list_filter = ['is_active', 'is_revoked', 'created_at']
    search_fields = ['name', 'workspace__name', 'key']
    readonly_fields = ['key', 'created_at', 'last_used_at', 'usage_count']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'name', 'created_by')
        }),
        ('Key', {
            'fields': ('key',)
        }),
        ('Permissions', {
            'fields': ('scopes', 'rate_limit_per_hour')
        }),
        ('Status', {
            'fields': ('is_active', 'is_revoked', 'expires_at')
        }),
        ('Usage Statistics', {
            'fields': ('usage_count', 'last_used_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    """Admin interface for webhooks."""

    list_display = [
        'integration', 'webhook_url', 'is_active',
        'total_deliveries', 'successful_deliveries', 'failed_deliveries',
        'last_delivery_at'
    ]
    list_filter = ['is_active', 'created_at']
    search_fields = ['integration__name', 'webhook_url']
    readonly_fields = [
        'total_deliveries', 'successful_deliveries', 'failed_deliveries',
        'last_delivery_at', 'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('integration', 'webhook_url', 'webhook_secret')
        }),
        ('Events', {
            'fields': ('events', 'is_active')
        }),
        ('Statistics', {
            'fields': (
                'total_deliveries', 'successful_deliveries', 'failed_deliveries',
                'last_delivery_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WebhookDelivery)
class WebhookDeliveryAdmin(admin.ModelAdmin):
    """Admin interface for webhook deliveries."""

    list_display = [
        'webhook', 'event_type', 'status', 'status_code',
        'attempt_count', 'duration_ms', 'created_at', 'delivered_at'
    ]
    list_filter = ['status', 'event_type', 'created_at']
    search_fields = ['webhook__integration__name', 'event_type']
    readonly_fields = ['created_at', 'delivered_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Webhook', {
            'fields': ('webhook',)
        }),
        ('Event', {
            'fields': ('event_type', 'payload')
        }),
        ('Delivery Status', {
            'fields': ('status', 'status_code', 'attempt_count', 'duration_ms')
        }),
        ('Response', {
            'fields': ('response_body', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'delivered_at')
        }),
    )


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    """Admin interface for integration logs."""

    list_display = [
        'integration', 'action', 'status', 'duration_ms', 'created_at'
    ]
    list_filter = ['status', 'action', 'created_at']
    search_fields = ['integration__name', 'action']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Integration', {
            'fields': ('integration',)
        }),
        ('Action', {
            'fields': ('action', 'status')
        }),
        ('Details', {
            'fields': ('request_data', 'response_data', 'error_message')
        }),
        ('Performance', {
            'fields': ('duration_ms',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

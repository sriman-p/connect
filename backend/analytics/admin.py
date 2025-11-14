"""
Analytics Admin Interface
"""

from django.contrib import admin
from .models import AnalyticsEvent, UsageMetric


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(admin.ModelAdmin):
    """Admin interface for analytics events."""

    list_display = [
        'event_type', 'event_name', 'user', 'workspace',
        'duration_ms', 'created_at'
    ]
    list_filter = ['event_type', 'workspace', 'created_at']
    search_fields = ['event_name', 'user__email', 'session_id']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Event Information', {
            'fields': ('workspace', 'user', 'event_type', 'event_name')
        }),
        ('Context', {
            'fields': ('session_id', 'ip_address', 'user_agent', 'referrer')
        }),
        ('Performance', {
            'fields': ('duration_ms',)
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at')
        }),
    )


@admin.register(UsageMetric)
class UsageMetricAdmin(admin.ModelAdmin):
    """Admin interface for usage metrics."""

    list_display = [
        'metric_name', 'workspace', 'metric_type',
        'value', 'unit', 'date', 'period_type'
    ]
    list_filter = ['metric_type', 'period_type', 'workspace', 'date']
    search_fields = ['metric_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'

    fieldsets = (
        ('Metric Information', {
            'fields': ('workspace', 'metric_type', 'metric_name')
        }),
        ('Value', {
            'fields': ('value', 'unit')
        }),
        ('Time Period', {
            'fields': ('date', 'period_type')
        }),
        ('Breakdown', {
            'fields': ('breakdown',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

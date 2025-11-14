"""
AI Admin Interface
"""

from django.contrib import admin
from .models import AIInteraction, AISmartSuggestion, AIModelConfig


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    """Admin interface for AI interactions."""

    list_display = [
        'interaction_type', 'user', 'workspace', 'model_used',
        'tokens_used', 'duration_ms', 'rating', 'created_at'
    ]
    list_filter = ['interaction_type', 'model_used', 'rating', 'created_at']
    search_fields = ['user__email', 'prompt', 'response']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'user', 'interaction_type')
        }),
        ('Content', {
            'fields': ('prompt', 'response')
        }),
        ('Model Configuration', {
            'fields': ('model_used', 'temperature', 'max_tokens')
        }),
        ('Usage Metrics', {
            'fields': ('tokens_used', 'duration_ms')
        }),
        ('Context', {
            'fields': ('context_data', 'content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('User Feedback', {
            'fields': ('rating', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AISmartSuggestion)
class AISmartSuggestionAdmin(admin.ModelAdmin):
    """Admin interface for AI smart suggestions."""

    list_display = [
        'suggestion_type', 'user', 'workspace', 'confidence_score',
        'status', 'created_at', 'accepted_at'
    ]
    list_filter = ['suggestion_type', 'status', 'created_at']
    search_fields = ['user__email', 'suggestion', 'reasoning']
    readonly_fields = ['created_at', 'accepted_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'user', 'suggestion_type')
        }),
        ('Suggestion', {
            'fields': ('suggestion', 'confidence_score', 'reasoning')
        }),
        ('Related Object', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'accepted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    """Admin interface for AI model configuration."""

    list_display = [
        'workspace', 'model_name', 'is_active',
        'requests_today', 'tokens_this_month',
        'daily_request_limit', 'monthly_token_limit'
    ]
    list_filter = ['model_name', 'is_active', 'created_at']
    search_fields = ['workspace__name']
    readonly_fields = ['created_at', 'updated_at', 'requests_today', 'tokens_this_month', 'last_reset_date']

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'model_name', 'api_key', 'is_active')
        }),
        ('Default Parameters', {
            'fields': ('default_temperature', 'default_max_tokens', 'default_top_p', 'default_top_k')
        }),
        ('Usage Limits', {
            'fields': ('daily_request_limit', 'monthly_token_limit')
        }),
        ('Current Usage', {
            'fields': ('requests_today', 'tokens_this_month', 'last_reset_date')
        }),
        ('Features', {
            'fields': (
                'enable_completions', 'enable_suggestions', 'enable_summaries',
                'enable_translations', 'enable_code_review'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

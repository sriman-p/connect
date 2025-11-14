"""
AI Serializers
"""

from rest_framework import serializers
from .models import AIInteraction, AISmartSuggestion, AIModelConfig


class AIInteractionSerializer(serializers.ModelSerializer):
    """Serializer for AI interactions."""

    class Meta:
        model = AIInteraction
        fields = [
            'id', 'workspace', 'user', 'interaction_type',
            'prompt', 'response', 'model_used',
            'tokens_used', 'duration_ms', 'temperature', 'max_tokens',
            'context_data', 'rating', 'feedback', 'created_at'
        ]
        read_only_fields = [
            'id', 'tokens_used', 'duration_ms', 'created_at'
        ]


class AISmartSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for AI smart suggestions."""

    class Meta:
        model = AISmartSuggestion
        fields = [
            'id', 'workspace', 'user', 'suggestion_type',
            'suggestion', 'confidence_score', 'reasoning',
            'status', 'accepted_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'confidence_score', 'reasoning', 'accepted_at', 'created_at'
        ]


class AIModelConfigSerializer(serializers.ModelSerializer):
    """Serializer for AI model configuration."""

    class Meta:
        model = AIModelConfig
        fields = [
            'id', 'workspace', 'model_name', 'api_key',
            'default_temperature', 'default_max_tokens',
            'default_top_p', 'default_top_k',
            'daily_request_limit', 'monthly_token_limit',
            'requests_today', 'tokens_this_month', 'last_reset_date',
            'enable_completions', 'enable_suggestions', 'enable_summaries',
            'enable_translations', 'enable_code_review',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'requests_today', 'tokens_this_month', 'last_reset_date',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'api_key': {'write_only': True}
        }


class CompletionRequestSerializer(serializers.Serializer):
    """Serializer for completion requests."""

    prompt = serializers.CharField()
    temperature = serializers.FloatField(default=0.7, min_value=0.0, max_value=1.0)
    max_tokens = serializers.IntegerField(required=False, min_value=1)
    context = serializers.JSONField(required=False)


class SummaryRequestSerializer(serializers.Serializer):
    """Serializer for summary requests."""

    content = serializers.CharField()
    max_length = serializers.IntegerField(default=200, min_value=50)


class SuggestionRequestSerializer(serializers.Serializer):
    """Serializer for suggestion requests."""

    context = serializers.CharField()
    suggestion_type = serializers.ChoiceField(
        choices=['task', 'reply', 'tag', 'priority']
    )
    count = serializers.IntegerField(default=3, min_value=1, max_value=10)


class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for analysis requests."""

    content = serializers.CharField()
    analysis_type = serializers.ChoiceField(
        choices=['sentiment', 'keywords', 'summary']
    )


class TranslationRequestSerializer(serializers.Serializer):
    """Serializer for translation requests."""

    content = serializers.CharField()
    target_language = serializers.CharField()


class CodeReviewRequestSerializer(serializers.Serializer):
    """Serializer for code review requests."""

    code = serializers.CharField()
    language = serializers.CharField()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat requests."""

    messages = serializers.ListField(
        child=serializers.DictField()
    )

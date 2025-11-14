"""
Analytics Serializers
"""

from rest_framework import serializers
from .models import AnalyticsEvent, UsageMetric


class AnalyticsEventSerializer(serializers.ModelSerializer):
    """Serializer for analytics events."""

    class Meta:
        model = AnalyticsEvent
        fields = [
            'id', 'workspace', 'user', 'event_type', 'event_name',
            'metadata', 'session_id', 'ip_address', 'user_agent',
            'referrer', 'duration_ms', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class UsageMetricSerializer(serializers.ModelSerializer):
    """Serializer for usage metrics."""

    class Meta:
        model = UsageMetric
        fields = [
            'id', 'workspace', 'metric_type', 'metric_name',
            'value', 'unit', 'date', 'period_type', 'breakdown',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics."""

    total_users = serializers.IntegerField()
    active_users_today = serializers.IntegerField()
    total_projects = serializers.IntegerField()
    total_issues = serializers.IntegerField()
    issues_closed_today = serializers.IntegerField()
    documents_created_today = serializers.IntegerField()
    meetings_today = serializers.IntegerField()

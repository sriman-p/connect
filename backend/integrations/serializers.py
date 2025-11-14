"""
Integrations Serializers
"""

from rest_framework import serializers
from .models import Integration, APIKey, Webhook, WebhookDelivery, IntegrationLog


class IntegrationSerializer(serializers.ModelSerializer):
    """Serializer for integrations."""

    class Meta:
        model = Integration
        fields = [
            'id', 'workspace', 'name', 'integration_type', 'config',
            'is_active', 'auto_sync', 'sync_interval_minutes',
            'sync_status', 'sync_error', 'last_synced_at',
            'installed_by', 'installed_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'sync_status', 'sync_error', 'last_synced_at',
            'installed_at', 'updated_at'
        ]
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True},
        }


class APIKeySerializer(serializers.ModelSerializer):
    """Serializer for API keys."""

    class Meta:
        model = APIKey
        fields = [
            'id', 'workspace', 'name', 'key', 'scopes',
            'rate_limit_per_hour', 'last_used_at', 'usage_count',
            'expires_at', 'is_active', 'is_revoked',
            'created_by', 'created_at'
        ]
        read_only_fields = [
            'id', 'key', 'last_used_at', 'usage_count', 'created_at'
        ]


class WebhookSerializer(serializers.ModelSerializer):
    """Serializer for webhooks."""

    class Meta:
        model = Webhook
        fields = [
            'id', 'integration', 'webhook_url', 'webhook_secret',
            'events', 'is_active', 'total_deliveries',
            'successful_deliveries', 'failed_deliveries',
            'last_delivery_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_deliveries', 'successful_deliveries',
            'failed_deliveries', 'last_delivery_at', 'created_at', 'updated_at'
        ]


class WebhookDeliverySerializer(serializers.ModelSerializer):
    """Serializer for webhook deliveries."""

    class Meta:
        model = WebhookDelivery
        fields = [
            'id', 'webhook', 'event_type', 'payload', 'status',
            'status_code', 'response_body', 'error_message',
            'attempt_count', 'duration_ms', 'created_at', 'delivered_at'
        ]
        read_only_fields = ['id', 'created_at', 'delivered_at']


class IntegrationLogSerializer(serializers.ModelSerializer):
    """Serializer for integration logs."""

    class Meta:
        model = IntegrationLog
        fields = [
            'id', 'integration', 'action', 'status',
            'request_data', 'response_data', 'error_message',
            'duration_ms', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

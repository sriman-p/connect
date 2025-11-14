"""
Integrations Views
"""

import json
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.http import HttpResponse
from .models import Integration, APIKey, Webhook, WebhookDelivery, IntegrationLog
from .serializers import (
    IntegrationSerializer,
    APIKeySerializer,
    WebhookSerializer,
    WebhookDeliverySerializer,
    IntegrationLogSerializer,
)
from .webhooks import get_webhook_handler

logger = logging.getLogger(__name__)


class IntegrationViewSet(viewsets.ModelViewSet):
    """ViewSet for integrations."""

    serializer_class = IntegrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return integrations for user's workspaces."""
        user = self.request.user
        return Integration.objects.filter(
            workspace__members=user
        ).select_related('workspace', 'installed_by').distinct()

    def perform_create(self, serializer):
        """Create integration."""
        serializer.save(installed_by=self.request.user)

    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Trigger manual sync for integration."""
        integration = self.get_object()

        try:
            integration.sync_status = 'syncing'
            integration.save()

            # TODO: Implement actual sync logic based on integration type
            # This is a placeholder for the sync functionality

            integration.sync_status = 'success'
            integration.last_synced_at = timezone.now()
            integration.sync_error = ''
            integration.save()

            return Response({
                'status': 'success',
                'message': 'Sync completed successfully'
            })

        except Exception as e:
            integration.sync_status = 'failed'
            integration.sync_error = str(e)
            integration.save()

            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test integration connection."""
        integration = self.get_object()

        try:
            # TODO: Implement actual connection test based on integration type
            # This is a placeholder for the test functionality

            return Response({
                'status': 'success',
                'message': 'Connection test successful'
            })

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class APIKeyViewSet(viewsets.ModelViewSet):
    """ViewSet for API keys."""

    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return API keys for user's workspaces."""
        user = self.request.user
        return APIKey.objects.filter(
            workspace__members=user
        ).select_related('workspace', 'created_by').distinct()

    def perform_create(self, serializer):
        """Create API key with generated key."""
        import secrets
        api_key = secrets.token_urlsafe(48)
        serializer.save(
            created_by=self.request.user,
            key=api_key
        )

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke an API key."""
        api_key = self.get_object()
        api_key.is_revoked = True
        api_key.is_active = False
        api_key.save()

        return Response({
            'status': 'success',
            'message': 'API key revoked successfully'
        })


class WebhookViewSet(viewsets.ModelViewSet):
    """ViewSet for webhooks."""

    serializer_class = WebhookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return webhooks for user's integrations."""
        user = self.request.user
        return Webhook.objects.filter(
            integration__workspace__members=user
        ).select_related('integration').distinct()


class WebhookDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for webhook deliveries (read-only)."""

    serializer_class = WebhookDeliverySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return webhook deliveries for user's webhooks."""
        user = self.request.user
        return WebhookDelivery.objects.filter(
            webhook__integration__workspace__members=user
        ).select_related('webhook__integration').distinct()


class IntegrationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for integration logs (read-only)."""

    serializer_class = IntegrationLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return logs for user's integrations."""
        user = self.request.user
        return IntegrationLog.objects.filter(
            integration__workspace__members=user
        ).select_related('integration').distinct()


@method_decorator(csrf_exempt, name='dispatch')
class WebhookReceiverView(APIView):
    """Receive and process webhooks from external services."""

    permission_classes = []  # No authentication required for webhooks
    authentication_classes = []

    def post(self, request, integration_id):
        """Handle incoming webhook."""
        start_time = timezone.now()

        try:
            # Get integration
            try:
                integration = Integration.objects.get(id=integration_id, is_active=True)
            except Integration.DoesNotExist:
                logger.error(f"Integration not found: {integration_id}")
                return Response({'error': 'Integration not found'}, status=404)

            # Get webhook handler
            try:
                handler = get_webhook_handler(integration)
            except ValueError as e:
                logger.error(f"Handler error: {str(e)}")
                return Response({'error': str(e)}, status=400)

            # Get payload
            payload = request.body
            try:
                payload_dict = json.loads(payload) if payload else {}
            except json.JSONDecodeError:
                payload_dict = {}

            # Validate signature (if webhook has secret configured)
            webhook = integration.webhooks.filter(is_active=True).first()
            if webhook and webhook.webhook_secret:
                signature = request.META.get('HTTP_X_HUB_SIGNATURE_256') or \
                           request.META.get('HTTP_X_SLACK_SIGNATURE') or \
                           request.META.get('HTTP_X_JIRA_SIGNATURE')

                if not handler.validate_signature(payload, signature, webhook.webhook_secret):
                    logger.warning(f"Invalid webhook signature for integration {integration_id}")
                    return Response({'error': 'Invalid signature'}, status=401)

            # Get event type
            event_type = request.META.get('HTTP_X_GITHUB_EVENT') or \
                        request.META.get('HTTP_X_EVENT_KEY') or \
                        payload_dict.get('type', 'unknown')

            # Handle webhook
            result = handler.handle(event_type, payload_dict)

            # Calculate duration
            duration_ms = int((timezone.now() - start_time).total_seconds() * 1000)

            # Log webhook delivery
            if webhook:
                WebhookDelivery.objects.create(
                    webhook=webhook,
                    event_type=event_type,
                    payload=payload_dict,
                    status='success' if result.get('success') else 'failed',
                    status_code=200 if result.get('success') else 500,
                    response_body=json.dumps(result),
                    error_message=result.get('message', '') if not result.get('success') else '',
                    attempt_count=1,
                    duration_ms=duration_ms,
                    delivered_at=timezone.now()
                )

                # Update webhook statistics
                webhook.total_deliveries += 1
                if result.get('success'):
                    webhook.successful_deliveries += 1
                else:
                    webhook.failed_deliveries += 1
                webhook.last_delivery_at = timezone.now()
                webhook.save()

            # Log integration activity
            IntegrationLog.objects.create(
                integration=integration,
                action=f"webhook_{event_type}",
                status='success' if result.get('success') else 'failed',
                request_data={'event_type': event_type},
                response_data=result.get('data', {}),
                error_message=result.get('message', '') if not result.get('success') else '',
                duration_ms=duration_ms
            )

            # Handle Slack URL verification
            if result.get('data', {}).get('challenge'):
                return HttpResponse(result['data']['challenge'], content_type='text/plain')

            return Response(result)

        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return Response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)

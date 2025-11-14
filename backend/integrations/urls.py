"""
Integrations URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    IntegrationViewSet,
    APIKeyViewSet,
    WebhookViewSet,
    WebhookDeliveryViewSet,
    IntegrationLogViewSet,
    WebhookReceiverView,
)

router = DefaultRouter()
router.register(r'integrations', IntegrationViewSet, basename='integration')
router.register(r'api-keys', APIKeyViewSet, basename='api-key')
router.register(r'webhooks', WebhookViewSet, basename='webhook')
router.register(r'webhook-deliveries', WebhookDeliveryViewSet, basename='webhook-delivery')
router.register(r'logs', IntegrationLogViewSet, basename='integration-log')

urlpatterns = [
    path('', include(router.urls)),
    path('webhook/<int:integration_id>/', WebhookReceiverView.as_view(), name='webhook-receiver'),
]

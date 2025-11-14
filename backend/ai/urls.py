"""
AI URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIInteractionViewSet,
    AISmartSuggestionViewSet,
    AIModelConfigViewSet,
    AIServiceViewSet,
)

router = DefaultRouter()
router.register(r'interactions', AIInteractionViewSet, basename='ai-interaction')
router.register(r'suggestions', AISmartSuggestionViewSet, basename='ai-suggestion')
router.register(r'configs', AIModelConfigViewSet, basename='ai-config')
router.register(r'service', AIServiceViewSet, basename='ai-service')

urlpatterns = [
    path('', include(router.urls)),
]

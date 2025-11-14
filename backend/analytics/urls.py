"""
Analytics URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsEventViewSet, UsageMetricViewSet, AnalyticsDashboardViewSet

app_name = 'analytics'

router = DefaultRouter()
router.register(r'events', AnalyticsEventViewSet, basename='event')
router.register(r'metrics', UsageMetricViewSet, basename='metric')
router.register(r'dashboard', AnalyticsDashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]

"""
Approvals URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ApprovalWorkflowViewSet,
    ApprovalStepViewSet,
    ApprovalRequestViewSet,
    ApprovalActionViewSet,
)

app_name = 'approvals'

router = DefaultRouter()
router.register(r'workflows', ApprovalWorkflowViewSet, basename='workflow')
router.register(r'steps', ApprovalStepViewSet, basename='step')
router.register(r'requests', ApprovalRequestViewSet, basename='request')
router.register(r'actions', ApprovalActionViewSet, basename='action')

urlpatterns = [
    path('', include(router.urls)),
]

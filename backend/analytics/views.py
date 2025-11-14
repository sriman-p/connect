"""
Analytics Views
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q
from .models import AnalyticsEvent, UsageMetric
from .serializers import (
    AnalyticsEventSerializer,
    UsageMetricSerializer,
    DashboardStatsSerializer,
)
from users.models import User
from projects.models import Project
from issues.models import Issue
from documents.models import Document
from meetings.models import Meeting


class AnalyticsEventViewSet(viewsets.ModelViewSet):
    """ViewSet for analytics events."""

    serializer_class = AnalyticsEventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return events for user's workspaces."""
        user = self.request.user
        return AnalyticsEvent.objects.filter(
            workspace__members=user
        ).select_related('user', 'workspace').distinct()

    def perform_create(self, serializer):
        """Create analytics event."""
        serializer.save(
            user=self.request.user,
            ip_address=self.request.META.get('REMOTE_ADDR'),
            user_agent=self.request.META.get('HTTP_USER_AGENT', ''),
        )


class UsageMetricViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for usage metrics (read-only)."""

    serializer_class = UsageMetricSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return metrics for user's workspaces."""
        user = self.request.user
        return UsageMetric.objects.filter(
            workspace__members=user
        ).select_related('workspace').distinct()


class AnalyticsDashboardViewSet(viewsets.ViewSet):
    """ViewSet for analytics dashboard."""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics."""
        user = request.user
        today = timezone.now().date()
        
        # Get user's workspaces
        workspace_ids = user.workspace_memberships.values_list('workspace_id', flat=True)

        # Calculate stats
        total_users = User.objects.filter(
            workspace_memberships__workspace_id__in=workspace_ids
        ).distinct().count()

        active_today = AnalyticsEvent.objects.filter(
            workspace_id__in=workspace_ids,
            created_at__date=today
        ).values('user').distinct().count()

        total_projects = Project.objects.filter(
            workspace_id__in=workspace_ids
        ).count()

        total_issues = Issue.objects.filter(
            workspace_id__in=workspace_ids
        ).count()

        issues_closed_today = Issue.objects.filter(
            workspace_id__in=workspace_ids,
            completed_at__date=today
        ).count()

        docs_today = Document.objects.filter(
            workspace_id__in=workspace_ids,
            created_at__date=today
        ).count()

        meetings_today = Meeting.objects.filter(
            workspace_id__in=workspace_ids,
            start_time__date=today
        ).count()

        stats = {
            'total_users': total_users,
            'active_users_today': active_today,
            'total_projects': total_projects,
            'total_issues': total_issues,
            'issues_closed_today': issues_closed_today,
            'documents_created_today': docs_today,
            'meetings_today': meetings_today,
        }

        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def activity(self, request):
        """Get recent activity."""
        user = request.user
        workspace_ids = user.workspace_memberships.values_list('workspace_id', flat=True)
        
        # Get last 7 days of activity
        last_week = timezone.now() - timedelta(days=7)
        
        activity = AnalyticsEvent.objects.filter(
            workspace_id__in=workspace_ids,
            created_at__gte=last_week
        ).values(
            'created_at__date'
        ).annotate(
            count=Count('id')
        ).order_by('created_at__date')

        return Response(activity)

    @action(detail=False, methods=['get'])
    def features(self, request):
        """Get feature usage statistics."""
        user = request.user
        workspace_ids = user.workspace_memberships.values_list('workspace_id', flat=True)
        
        # Get last 30 days
        last_month = timezone.now() - timedelta(days=30)
        
        features = AnalyticsEvent.objects.filter(
            workspace_id__in=workspace_ids,
            created_at__gte=last_month,
            event_type='feature_usage'
        ).values('event_name').annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        return Response(features)

"""
Analytics Models
Track usage metrics and generate insights
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import User
from workspaces.models import Workspace


class AnalyticsEvent(models.Model):
    """Track user events for analytics."""

    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('feature_usage', 'Feature Usage'),
        ('api_call', 'API Call'),
        ('search', 'Search'),
        ('document_edit', 'Document Edit'),
        ('issue_create', 'Issue Create'),
        ('meeting_join', 'Meeting Join'),
        ('file_upload', 'File Upload'),
        ('approval_action', 'Approval Action'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='analytics_events')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    event_name = models.CharField(max_length=200)

    # Generic relation to any object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Event metadata
    metadata = models.JSONField(default=dict, blank=True)

    # Context
    session_id = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, max_length=500)

    # Performance
    duration_ms = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'event_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['session_id']),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.event_name}"


class UsageMetric(models.Model):
    """Aggregated usage metrics."""

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='usage_metrics')
    metric_type = models.CharField(max_length=50, db_index=True)
    metric_name = models.CharField(max_length=200)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)
    date = models.DateField(db_index=True)
    period_type = models.CharField(max_length=20)
    breakdown = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['workspace', 'metric_type', 'date', 'period_type']

    def __str__(self):
        return f"{self.metric_name} - {self.date}"

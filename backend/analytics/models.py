"""
Analytics Models
Advanced analytics, reporting, and business intelligence
"""

from django.db import models
from django.contrib.postgres.fields import ArrayField
from users.models import User
from workspaces.models import Workspace
from projects.models import Project


class Dashboard(models.Model):
    """Custom analytics dashboard."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='dashboards'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Dashboard configuration (widgets, layout, etc.)
    config = models.JSONField(default=dict)

    # Permissions
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False)
    shared_with = models.ManyToManyField(User, related_name='shared_dashboards', blank=True)

    # Default dashboard for workspace
    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'is_default']),
        ]

    def __str__(self):
        return self.name


class Widget(models.Model):
    """Dashboard widget."""

    WIDGET_TYPE_CHOICES = [
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('metric', 'Metric'),
        ('list', 'List'),
        ('calendar', 'Calendar'),
        ('timeline', 'Timeline'),
        ('funnel', 'Funnel'),
        ('gauge', 'Gauge'),
    ]

    CHART_TYPE_CHOICES = [
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('scatter', 'Scatter Plot'),
        ('heatmap', 'Heatmap'),
    ]

    dashboard = models.ForeignKey(
        Dashboard,
        on_delete=models.CASCADE,
        related_name='widgets'
    )

    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPE_CHOICES)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPE_CHOICES, blank=True)

    # Widget configuration and data source
    config = models.JSONField(default=dict)
    data_source = models.CharField(max_length=100)  # e.g., 'issues', 'projects'
    filters = models.JSONField(default=dict)

    # Position and size on dashboard
    position_x = models.IntegerField(default=0)
    position_y = models.IntegerField(default=0)
    width = models.IntegerField(default=4)
    height = models.IntegerField(default=3)

    # Refresh settings
    auto_refresh = models.BooleanField(default=False)
    refresh_interval_seconds = models.IntegerField(default=300)  # 5 minutes

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position_y', 'position_x']

    def __str__(self):
        return f"{self.title} ({self.widget_type})"


class Report(models.Model):
    """Custom report."""

    REPORT_TYPE_CHOICES = [
        ('project_summary', 'Project Summary'),
        ('team_performance', 'Team Performance'),
        ('time_analysis', 'Time Analysis'),
        ('velocity', 'Velocity Report'),
        ('burndown', 'Burndown Chart'),
        ('budget', 'Budget Report'),
        ('custom', 'Custom Report'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='reports'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    report_type = models.CharField(max_length=30, choices=REPORT_TYPE_CHOICES)

    # Report configuration
    config = models.JSONField(default=dict)
    filters = models.JSONField(default=dict)

    # Date range
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)

    # Scheduling
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
        ],
        blank=True
    )
    recipients = models.ManyToManyField(User, related_name='scheduled_reports', blank=True)

    # Creator
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Metric(models.Model):
    """Tracked metric/KPI."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='metrics'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='metrics'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Metric type and calculation
    metric_type = models.CharField(
        max_length=50,
        choices=[
            ('count', 'Count'),
            ('sum', 'Sum'),
            ('average', 'Average'),
            ('percentage', 'Percentage'),
            ('custom', 'Custom Formula'),
        ]
    )

    # Data source and calculation
    data_source = models.CharField(max_length=100)
    calculation_formula = models.TextField(blank=True)

    # Target values
    target_value = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Unit (e.g., hours, dollars, issues)
    unit = models.CharField(max_length=20, blank=True)

    # Trend direction (higher or lower is better)
    trend_direction = models.CharField(
        max_length=10,
        choices=[
            ('up', 'Higher is Better'),
            ('down', 'Lower is Better'),
        ],
        default='up'
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class MetricSnapshot(models.Model):
    """Historical metric value snapshot."""

    metric = models.ForeignKey(
        Metric,
        on_delete=models.CASCADE,
        related_name='snapshots'
    )

    value = models.DecimalField(max_digits=12, decimal_places=2)
    metadata = models.JSONField(default=dict, blank=True)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric', 'recorded_at']),
        ]

    def __str__(self):
        return f"{self.metric.name}: {self.value} at {self.recorded_at}"

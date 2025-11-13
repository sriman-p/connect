"""
Integrations Models
Third-party integrations and API keys
"""

from django.db import models
from users.models import User
from workspaces.models import Workspace


class Integration(models.Model):
    """Third-party integration configuration."""

    INTEGRATION_TYPE_CHOICES = [
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('bitbucket', 'Bitbucket'),
        ('jira', 'Jira'),
        ('slack', 'Slack'),
        ('teams', 'Microsoft Teams'),
        ('google', 'Google Workspace'),
        ('zoom', 'Zoom'),
        ('calendar', 'Calendar'),
        ('storage', 'Cloud Storage'),
        ('sso', 'Single Sign-On'),
        ('custom', 'Custom Integration'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='integrations'
    )

    name = models.CharField(max_length=100)
    integration_type = models.CharField(max_length=50, choices=INTEGRATION_TYPE_CHOICES)

    # Configuration
    config = models.JSONField(default=dict)  # API keys, webhooks, etc.

    # OAuth tokens (encrypted in production)
    access_token = models.CharField(max_length=500, blank=True)
    refresh_token = models.CharField(max_length=500, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    auto_sync = models.BooleanField(default=False)
    sync_interval_minutes = models.IntegerField(default=60)

    # Sync status
    last_synced_at = models.DateTimeField(null=True, blank=True)
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('syncing', 'Syncing'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    sync_error = models.TextField(blank=True)

    installed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    installed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-installed_at']

    def __str__(self):
        return f"{self.name} ({self.integration_type})"


class APIKey(models.Model):
    """API key for programmatic access."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='api_keys'
    )

    name = models.CharField(max_length=100)
    key = models.CharField(max_length=64, unique=True)  # Hashed key

    # Permissions
    scopes = models.JSONField(default=list)  # List of allowed scopes

    # Rate limiting
    rate_limit_per_hour = models.IntegerField(default=1000)

    # Usage stats
    last_used_at = models.DateTimeField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    is_revoked = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class IntegrationLog(models.Model):
    """Integration activity log."""

    integration = models.ForeignKey(
        Integration,
        on_delete=models.CASCADE,
        related_name='logs'
    )

    # Action
    action = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
        ]
    )

    # Details
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)

    # Metadata
    duration_ms = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.integration.name} - {self.action}"

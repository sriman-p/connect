"""
Automations Models
Workflow automation, rules, and webhooks
"""

from django.db import models
from users.models import User
from workspaces.models import Workspace


class Automation(models.Model):
    """Automation rule."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='automations'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Trigger
    trigger_type = models.CharField(
        max_length=50,
        choices=[
            ('issue_created', 'Issue Created'),
            ('issue_updated', 'Issue Updated'),
            ('issue_status_changed', 'Issue Status Changed'),
            ('comment_added', 'Comment Added'),
            ('file_uploaded', 'File Uploaded'),
            ('meeting_scheduled', 'Meeting Scheduled'),
            ('approval_requested', 'Approval Requested'),
            ('time_based', 'Time Based'),
            ('webhook', 'Webhook'),
        ]
    )

    trigger_config = models.JSONField(default=dict)  # Trigger conditions

    # Actions
    actions = models.JSONField(default=list)  # List of actions to perform

    # Status
    is_active = models.BooleanField(default=True)

    # Execution stats
    execution_count = models.IntegerField(default=0)
    last_executed_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AutomationRun(models.Model):
    """Automation execution log."""

    automation = models.ForeignKey(
        Automation,
        on_delete=models.CASCADE,
        related_name='runs'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('success', 'Success'),
            ('failed', 'Failed'),
            ('partial', 'Partial Success'),
        ]
    )

    # Details
    trigger_data = models.JSONField(default=dict)
    actions_performed = models.JSONField(default=list)
    error_message = models.TextField(blank=True)

    # Metadata
    duration_ms = models.IntegerField(default=0)

    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.automation.name} - {self.status}"


class Webhook(models.Model):
    """Outgoing webhook."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='webhooks'
    )

    name = models.CharField(max_length=100)
    url = models.URLField()

    # Events to trigger on
    events = models.JSONField(default=list)  # List of event types

    # Authentication
    auth_type = models.CharField(
        max_length=20,
        choices=[
            ('none', 'None'),
            ('basic', 'Basic Auth'),
            ('bearer', 'Bearer Token'),
            ('api_key', 'API Key'),
        ],
        default='none'
    )
    auth_config = models.JSONField(default=dict, blank=True)

    # Settings
    is_active = models.BooleanField(default=True)
    retry_on_failure = models.BooleanField(default=True)
    max_retries = models.IntegerField(default=3)

    # Stats
    success_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)
    last_triggered_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class WebhookDelivery(models.Model):
    """Webhook delivery log."""

    webhook = models.ForeignKey(
        Webhook,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )

    # Event
    event_type = models.CharField(max_length=50)
    payload = models.JSONField()

    # Response
    status_code = models.IntegerField(null=True)
    response_body = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('success', 'Success'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    # Retries
    retry_count = models.IntegerField(default=0)
    next_retry_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    duration_ms = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Webhook deliveries'

    def __str__(self):
        return f"{self.webhook.name} - {self.event_type}"


class Template(models.Model):
    """Automation template."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='automation_templates'
    )

    name = models.CharField(max_length=100)
    description = models.TextField()

    # Template configuration
    config = models.JSONField()  # Complete automation config

    # Category
    category = models.CharField(
        max_length=50,
        choices=[
            ('onboarding', 'Onboarding'),
            ('notifications', 'Notifications'),
            ('assignments', 'Assignments'),
            ('escalations', 'Escalations'),
            ('integrations', 'Integrations'),
        ]
    )

    # Visibility
    is_public = models.BooleanField(default=False)
    is_official = models.BooleanField(default=False)

    # Usage stats
    usage_count = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-usage_count']

    def __str__(self):
        return self.name

"""
Notifications Models
Push notifications, email, and in-app notifications
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import User
from workspaces.models import Workspace


class Notification(models.Model):
    """User notification."""

    NOTIFICATION_TYPE_CHOICES = [
        # Mentions and comments
        ('mention', 'Mentioned in comment'),
        ('comment', 'New comment'),
        ('reply', 'Reply to comment'),

        # Issues
        ('issue_assigned', 'Issue assigned'),
        ('issue_updated', 'Issue updated'),
        ('issue_completed', 'Issue completed'),
        ('issue_comment', 'Issue comment'),

        # Projects
        ('project_invite', 'Project invitation'),
        ('project_updated', 'Project updated'),

        # Meetings
        ('meeting_invite', 'Meeting invitation'),
        ('meeting_reminder', 'Meeting reminder'),
        ('meeting_started', 'Meeting started'),
        ('meeting_cancelled', 'Meeting cancelled'),

        # Approvals
        ('approval_request', 'Approval requested'),
        ('approval_approved', 'Approval approved'),
        ('approval_rejected', 'Approval rejected'),
        ('approval_delegated', 'Approval delegated'),

        # Documents
        ('document_shared', 'Document shared'),
        ('document_comment', 'Document comment'),
        ('document_mention', 'Mentioned in document'),

        # Files
        ('file_shared', 'File shared'),
        ('file_comment', 'File comment'),

        # Workspace
        ('workspace_invite', 'Workspace invitation'),
        ('team_update', 'Team update'),

        # System
        ('system', 'System notification'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    # Recipient
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    # Notification details
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    # Actor (who triggered the notification)
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='triggered_notifications',
        null=True,
        blank=True
    )

    # Related object (generic foreign key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    # Action URL
    action_url = models.CharField(max_length=500, blank=True)

    # Status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Delivery channels
    sent_in_app = models.BooleanField(default=True)
    sent_email = models.BooleanField(default=False)
    sent_push = models.BooleanField(default=False)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at']),
            models.Index(fields=['workspace', 'created_at']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.notification_type} for {self.user.email}"


class NotificationPreference(models.Model):
    """User notification preferences."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )

    # Channel preferences
    enable_email = models.BooleanField(default=True)
    enable_push = models.BooleanField(default=True)
    enable_in_app = models.BooleanField(default=True)

    # Digest settings
    enable_daily_digest = models.BooleanField(default=False)
    digest_time = models.TimeField(null=True, blank=True)  # What time to send digest

    # Notification type preferences (JSON with type -> enabled mapping)
    type_preferences = models.JSONField(default=dict, blank=True)

    # Do Not Disturb
    dnd_enabled = models.BooleanField(default=False)
    dnd_start_time = models.TimeField(null=True, blank=True)
    dnd_end_time = models.TimeField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.email}"


class ActivityLog(models.Model):
    """Activity/audit log."""

    ACTION_CHOICES = [
        # User actions
        ('user.login', 'User logged in'),
        ('user.logout', 'User logged out'),
        ('user.updated', 'User updated profile'),

        # Workspace
        ('workspace.created', 'Workspace created'),
        ('workspace.updated', 'Workspace updated'),
        ('workspace.member_added', 'Member added'),
        ('workspace.member_removed', 'Member removed'),

        # Project
        ('project.created', 'Project created'),
        ('project.updated', 'Project updated'),
        ('project.deleted', 'Project deleted'),

        # Issue
        ('issue.created', 'Issue created'),
        ('issue.updated', 'Issue updated'),
        ('issue.assigned', 'Issue assigned'),
        ('issue.status_changed', 'Issue status changed'),
        ('issue.deleted', 'Issue deleted'),

        # Document
        ('document.created', 'Document created'),
        ('document.updated', 'Document updated'),
        ('document.shared', 'Document shared'),
        ('document.deleted', 'Document deleted'),

        # File
        ('file.uploaded', 'File uploaded'),
        ('file.downloaded', 'File downloaded'),
        ('file.shared', 'File shared'),
        ('file.deleted', 'File deleted'),

        # Meeting
        ('meeting.created', 'Meeting created'),
        ('meeting.started', 'Meeting started'),
        ('meeting.ended', 'Meeting ended'),
        ('meeting.cancelled', 'Meeting cancelled'),

        # Approval
        ('approval.submitted', 'Approval submitted'),
        ('approval.approved', 'Approval approved'),
        ('approval.rejected', 'Approval rejected'),

        # Message
        ('message.sent', 'Message sent'),
        ('message.edited', 'Message edited'),
        ('message.deleted', 'Message deleted'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='activity_logs',
        null=True,
        blank=True
    )

    # Actor
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_logs'
    )

    # Action
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()

    # Related object (generic foreign key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.action} by {self.user.email if self.user else 'System'}"

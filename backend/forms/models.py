"""
Forms and Surveys Models
Custom forms, surveys, and data collection
"""

from django.db import models
from users.models import User
from workspaces.models import Workspace


class Form(models.Model):
    """Custom form / survey."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='forms'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Form configuration
    fields = models.JSONField(default=list)  # List of field definitions
    settings = models.JSONField(default=dict)  # Form settings

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('closed', 'Closed'),
        ],
        default='draft'
    )

    # Permissions
    allow_anonymous = models.BooleanField(default=False)
    require_login = models.BooleanField(default=True)
    allowed_users = models.ManyToManyField(User, related_name='allowed_forms', blank=True)

    # Notifications
    notify_on_submission = models.BooleanField(default=True)
    notification_emails = models.JSONField(default=list, blank=True)

    # Limits
    max_submissions = models.IntegerField(null=True, blank=True)
    submission_count = models.IntegerField(default=0)

    # Timeline
    opens_at = models.DateTimeField(null=True, blank=True)
    closes_at = models.DateTimeField(null=True, blank=True)

    # Creator
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FormSubmission(models.Model):
    """Form submission response."""

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='submissions'
    )

    # Submitter (can be null for anonymous)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form_submissions'
    )

    # Response data
    data = models.JSONField()  # Field responses

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)

    # Status
    is_complete = models.BooleanField(default=True)
    is_spam = models.BooleanField(default=False)

    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission for {self.form.title}"


class Poll(models.Model):
    """Quick poll / vote."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='polls'
    )

    question = models.CharField(max_length=300)
    options = models.JSONField()  # List of options

    # Settings
    allow_multiple_votes = models.BooleanField(default=False)
    allow_add_options = models.BooleanField(default=False)
    anonymous_voting = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)
    closes_at = models.DateTimeField(null=True, blank=True)

    # Results
    total_votes = models.IntegerField(default=0)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question


class PollVote(models.Model):
    """Individual poll vote."""

    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE,
        related_name='votes'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,  # For anonymous votes
        related_name='poll_votes'
    )

    option_index = models.IntegerField()  # Index in options array

    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-voted_at']

    def __str__(self):
        return f"Vote on {self.poll.question}"

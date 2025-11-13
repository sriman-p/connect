"""
Approvals Models
Workflow approval system
"""

from django.db import models
from django.utils import timezone
from users.models import User
from workspaces.models import Workspace


class ApprovalWorkflow(models.Model):
    """Approval workflow template."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='approval_workflows'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Workflow type
    workflow_type = models.CharField(
        max_length=50,
        choices=[
            ('sequential', 'Sequential'),  # One approver at a time
            ('parallel', 'Parallel'),      # All approvers simultaneously
            ('any', 'Any'),                # Any one approver
        ],
        default='sequential'
    )

    # Auto-approval settings
    auto_approve_after_hours = models.IntegerField(null=True, blank=True)

    # Active status
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ApprovalStep(models.Model):
    """Step in an approval workflow."""

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='steps'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Step order (for sequential workflows)
    order = models.IntegerField(default=0)

    # Approvers for this step
    approvers = models.ManyToManyField(
        User,
        related_name='approval_steps'
    )

    # How many approvers needed (for parallel workflows)
    required_approvals = models.IntegerField(default=1)

    # Allow delegation
    allow_delegation = models.BooleanField(default=True)

    class Meta:
        ordering = ['workflow', 'order']
        unique_together = ['workflow', 'order']

    def __str__(self):
        return f"{self.workflow.name} - Step {self.order}"


class ApprovalRequest(models.Model):
    """Individual approval request."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    workflow = models.ForeignKey(
        ApprovalWorkflow,
        on_delete=models.CASCADE,
        related_name='requests'
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='approval_requests'
    )

    # Request details
    title = models.CharField(max_length=200)
    description = models.TextField()

    # What is being approved
    request_type = models.CharField(
        max_length=50,
        choices=[
            ('expense', 'Expense'),
            ('timeoff', 'Time Off'),
            ('purchase', 'Purchase Order'),
            ('document', 'Document'),
            ('project', 'Project'),
            ('other', 'Other'),
        ]
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')

    # Requester
    requested_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submitted_approvals'
    )

    # Current step (for sequential workflows)
    current_step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_requests'
    )

    # Attachments and data
    attachments = models.JSONField(default=list, blank=True)
    form_data = models.JSONField(default=dict, blank=True)

    # Amount (for financial approvals)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    currency = models.CharField(max_length=3, default='USD')

    # Deadlines
    due_date = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['requested_by', 'status']),
            models.Index(fields=['status', 'priority']),
        ]

    def __str__(self):
        return f"{self.title} - {self.status}"

    def is_overdue(self):
        """Check if request is overdue."""
        if self.due_date and self.status == 'pending':
            return timezone.now() > self.due_date
        return False


class ApprovalResponse(models.Model):
    """Individual approver response."""

    DECISION_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('delegated', 'Delegated'),
    ]

    request = models.ForeignKey(
        ApprovalRequest,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    step = models.ForeignKey(
        ApprovalStep,
        on_delete=models.CASCADE
    )

    approver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='approval_responses'
    )

    # Decision
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default='pending')
    comments = models.TextField(blank=True)

    # Delegation
    delegated_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_approvals'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['request', 'step', 'approver']

    def __str__(self):
        return f"{self.approver.email} - {self.decision}"

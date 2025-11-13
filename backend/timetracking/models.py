"""
Time Tracking Models
Time tracking, timesheets, and billable hours
"""

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from users.models import User
from workspaces.models import Workspace
from projects.models import Project
from issues.models import Issue


class TimeEntry(models.Model):
    """Time tracking entry."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )

    issue = models.ForeignKey(
        Issue,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='time_entries'
    )

    # User and description
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='time_entries'
    )
    description = models.TextField(blank=True)

    # Time tracking
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)

    # Manual time entry
    is_manual = models.BooleanField(default=False)

    # Billable
    is_billable = models.BooleanField(default=True)
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Status
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_time_entries'
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Invoicing
    is_invoiced = models.BooleanField(default=False)
    invoice_id = models.CharField(max_length=100, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['workspace', 'user', 'start_time']),
            models.Index(fields=['project', 'start_time']),
            models.Index(fields=['is_billable', 'is_invoiced']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.duration_minutes}min"

    def save(self, *args, **kwargs):
        # Calculate duration
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            self.duration_minutes = int(delta.total_seconds() / 60)

        # Calculate total amount
        if self.is_billable and self.hourly_rate:
            hours = Decimal(self.duration_minutes) / Decimal(60)
            self.total_amount = hours * self.hourly_rate

        super().save(*args, **kwargs)


class Timesheet(models.Model):
    """Weekly/monthly timesheet."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='timesheets'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timesheets'
    )

    # Period
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('weekly', 'Weekly'),
            ('biweekly', 'Bi-weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    start_date = models.DateField()
    end_date = models.DateField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='draft'
    )

    # Approval
    submitted_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timesheets'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    # Totals
    total_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    billable_hours = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['workspace', 'user', 'start_date', 'end_date']

    def __str__(self):
        return f"{self.user.email} - {self.start_date} to {self.end_date}"


class WorkSchedule(models.Model):
    """User work schedule."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='work_schedules'
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='work_schedules'
    )

    # Schedule details
    day_of_week = models.IntegerField(
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday'),
        ]
    )

    is_working_day = models.BooleanField(default=True)

    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    # Break time
    break_duration_minutes = models.IntegerField(default=60)

    # Expected hours per day
    expected_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8)

    class Meta:
        unique_together = ['user', 'workspace', 'day_of_week']
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.user.email} - {self.get_day_of_week_display()}"


class TimeoffRequest(models.Model):
    """Time off / vacation request."""

    TIMEOFF_TYPE_CHOICES = [
        ('vacation', 'Vacation'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Day'),
        ('bereavement', 'Bereavement'),
        ('parental', 'Parental Leave'),
        ('unpaid', 'Unpaid Leave'),
        ('other', 'Other'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='timeoff_requests'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timeoff_requests'
    )

    timeoff_type = models.CharField(max_length=20, choices=TIMEOFF_TYPE_CHOICES)
    reason = models.TextField(blank=True)

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    total_days = models.IntegerField(default=1)

    # Half day options
    is_half_day = models.BooleanField(default=False)
    half_day_period = models.CharField(
        max_length=10,
        choices=[
            ('morning', 'Morning'),
            ('afternoon', 'Afternoon'),
        ],
        blank=True
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )

    # Approval
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timeoffs'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.timeoff_type} ({self.start_date})"


class TimeoffBalance(models.Model):
    """User time off balance."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='timeoff_balances'
    )

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='timeoff_balances'
    )

    # Balance type
    timeoff_type = models.CharField(max_length=20, choices=TimeoffRequest.TIMEOFF_TYPE_CHOICES)

    # Year
    year = models.IntegerField()

    # Balances
    allocated_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    remaining_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    # Carry over from previous year
    carried_over_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'workspace', 'timeoff_type', 'year']
        ordering = ['-year']

    def __str__(self):
        return f"{self.user.email} - {self.timeoff_type} {self.year}"

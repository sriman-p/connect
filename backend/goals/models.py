"""
Goals and OKRs Models
Objectives and Key Results tracking
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from workspaces.models import Workspace
from projects.models import Project


class Objective(models.Model):
    """OKR Objective."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='objectives'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='objectives'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Ownership
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_objectives'
    )

    # Hierarchy
    parent_objective = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_objectives'
    )

    # Level
    level = models.CharField(
        max_length=20,
        choices=[
            ('company', 'Company'),
            ('team', 'Team'),
            ('individual', 'Individual'),
        ]
    )

    # Time period
    quarter = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(4)]
    )
    year = models.IntegerField()

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )

    # Progress (calculated from key results)
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Confidence level
    confidence = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Confidence level 1-10'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-quarter', '-created_at']

    def __str__(self):
        return self.title


class KeyResult(models.Model):
    """OKR Key Result."""

    objective = models.ForeignKey(
        Objective,
        on_delete=models.CASCADE,
        related_name='key_results'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Owner
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='key_results'
    )

    # Measurement type
    measurement_type = models.CharField(
        max_length=20,
        choices=[
            ('number', 'Numeric'),
            ('percentage', 'Percentage'),
            ('boolean', 'Yes/No'),
            ('currency', 'Currency'),
        ]
    )

    # Target values
    start_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Unit (e.g., users, dollars, hours)
    unit = models.CharField(max_length=50, blank=True)

    # Progress
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('on_track', 'On Track'),
            ('at_risk', 'At Risk'),
            ('behind', 'Behind'),
            ('completed', 'Completed'),
        ],
        default='on_track'
    )

    # Due date
    due_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} ({self.progress}%)"

    def update_progress(self):
        """Calculate progress based on current vs target value."""
        if self.target_value == 0:
            self.progress = 0
        else:
            achieved = self.current_value - self.start_value
            total = self.target_value - self.start_value
            if total > 0:
                self.progress = min(100, int((achieved / total) * 100))
            else:
                self.progress = 0


class Goal(models.Model):
    """Individual goal."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='goals'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='goals'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Category
    category = models.CharField(
        max_length=50,
        choices=[
            ('performance', 'Performance'),
            ('learning', 'Learning'),
            ('career', 'Career Development'),
            ('project', 'Project'),
            ('personal', 'Personal'),
        ]
    )

    # Timeline
    start_date = models.DateField()
    target_date = models.DateField()
    completed_at = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='not_started'
    )

    # Progress
    progress = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    # Privacy
    is_private = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-target_date']

    def __str__(self):
        return self.title


class Milestone(models.Model):
    """Goal or objective milestone."""

    goal = models.ForeignKey(
        Goal,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='milestones'
    )

    objective = models.ForeignKey(
        Objective,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='milestones'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    due_date = models.DateField()

    # Status
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return self.title

from django.db import models
from django.conf import settings


class Project(models.Model):
    """
    Project model for organizing work within a workspace.
    Linear-style project management with sprints and roadmaps.
    """

    # Status choices
    BACKLOG = 'backlog'
    PLANNED = 'planned'
    IN_PROGRESS = 'in_progress'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (BACKLOG, 'Backlog'),
        (PLANNED, 'Planned'),
        (IN_PROGRESS, 'In Progress'),
        (PAUSED, 'Paused'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]

    # Core fields
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='projects',
        help_text='Associated workspace'
    )
    name = models.CharField(
        max_length=200,
        help_text='Project name'
    )
    identifier = models.CharField(
        max_length=10,
        db_index=True,
        help_text='Project identifier (e.g., PROJ, ENG)'
    )
    description = models.TextField(
        max_length=2000,
        blank=True,
        default='',
        help_text='Project description'
    )

    # Status and dates
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=BACKLOG,
        db_index=True,
        help_text='Project status'
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text='Project start date'
    )
    target_date = models.DateField(
        null=True,
        blank=True,
        help_text='Project target completion date'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Project completion timestamp'
    )

    # Ownership and team
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='led_projects',
        help_text='Project lead'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_projects',
        help_text='Project creator'
    )

    # Settings
    color = models.CharField(
        max_length=7,
        default='#8B5CF6',
        help_text='Project color (hex)'
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text='Project icon name'
    )
    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Project is archived'
    )
    is_private = models.BooleanField(
        default=False,
        help_text='Project is private'
    )

    # Metrics (cached for performance)
    issue_count = models.IntegerField(
        default=0,
        help_text='Total issues in project'
    )
    completed_issue_count = models.IntegerField(
        default=0,
        help_text='Completed issues count'
    )
    progress = models.IntegerField(
        default=0,
        help_text='Project progress percentage (0-100)'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Project creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'projects'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created_at']
        unique_together = [['workspace', 'identifier']]
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['workspace', 'is_archived']),
            models.Index(fields=['identifier']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'target_date']),
        ]

    def __str__(self):
        return f"{self.identifier} - {self.name}"

    def update_metrics(self):
        """Update cached project metrics."""
        from issues.models import Issue

        issues = Issue.objects.filter(project=self)
        self.issue_count = issues.count()
        self.completed_issue_count = issues.filter(status='completed').count()

        if self.issue_count > 0:
            self.progress = int((self.completed_issue_count / self.issue_count) * 100)
        else:
            self.progress = 0

        self.save(update_fields=['issue_count', 'completed_issue_count', 'progress'])


class ProjectMember(models.Model):
    """
    Project membership for team members.
    Tracks who has access to specific projects.
    """

    # Relationships
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_members',
        help_text='Associated project'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='project_memberships',
        help_text='Member user'
    )

    # Timestamps
    added_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Member added timestamp'
    )

    class Meta:
        db_table = 'project_members'
        verbose_name = 'Project Member'
        verbose_name_plural = 'Project Members'
        unique_together = [['project', 'user']]
        indexes = [
            models.Index(fields=['project', 'user']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.project.name}"

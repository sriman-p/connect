from django.db import models
from django.conf import settings


class Label(models.Model):
    """
    Label model for categorizing issues.
    Similar to Linear's labels with colors.
    """

    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='labels',
        help_text='Associated workspace'
    )
    name = models.CharField(
        max_length=50,
        help_text='Label name'
    )
    description = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Label description'
    )
    color = models.CharField(
        max_length=7,
        default='#10B981',
        help_text='Label color (hex)'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Label creation timestamp'
    )

    class Meta:
        db_table = 'labels'
        verbose_name = 'Label'
        verbose_name_plural = 'Labels'
        ordering = ['name']
        unique_together = [['workspace', 'name']]
        indexes = [
            models.Index(fields=['workspace', 'name']),
        ]

    def __str__(self):
        return self.name


class Issue(models.Model):
    """
    Issue model for task/bug tracking.
    Linear-inspired with Kanban board support.
    """

    # Priority levels
    NO_PRIORITY = 'no_priority'
    URGENT = 'urgent'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

    PRIORITY_CHOICES = [
        (NO_PRIORITY, 'No Priority'),
        (URGENT, 'Urgent'),
        (HIGH, 'High'),
        (MEDIUM, 'Medium'),
        (LOW, 'Low'),
    ]

    # Status choices (Kanban columns)
    BACKLOG = 'backlog'
    TODO = 'todo'
    IN_PROGRESS = 'in_progress'
    IN_REVIEW = 'in_review'
    DONE = 'done'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (BACKLOG, 'Backlog'),
        (TODO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (IN_REVIEW, 'In Review'),
        (DONE, 'Done'),
        (CANCELLED, 'Cancelled'),
    ]

    # Issue type
    TASK = 'task'
    BUG = 'bug'
    FEATURE = 'feature'
    IMPROVEMENT = 'improvement'

    TYPE_CHOICES = [
        (TASK, 'Task'),
        (BUG, 'Bug'),
        (FEATURE, 'Feature'),
        (IMPROVEMENT, 'Improvement'),
    ]

    # Core fields
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='issues',
        help_text='Associated workspace'
    )
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='issues',
        help_text='Associated project'
    )
    identifier = models.CharField(
        max_length=20,
        db_index=True,
        help_text='Issue identifier (e.g., PROJ-123)'
    )
    title = models.CharField(
        max_length=300,
        help_text='Issue title'
    )
    description = models.TextField(
        blank=True,
        default='',
        help_text='Issue description (supports markdown)'
    )

    # Classification
    issue_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TASK,
        help_text='Issue type'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=NO_PRIORITY,
        db_index=True,
        help_text='Issue priority'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=BACKLOG,
        db_index=True,
        help_text='Issue status'
    )

    # Relationships
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_issues',
        help_text='Assigned user'
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_issues',
        help_text='Issue reporter'
    )
    labels = models.ManyToManyField(
        Label,
        blank=True,
        related_name='issues',
        help_text='Issue labels'
    )

    # Parent-child relationship for sub-issues
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_issues',
        help_text='Parent issue'
    )

    # Ordering and grouping
    sort_order = models.IntegerField(
        default=0,
        help_text='Display order within status column'
    )
    estimate = models.IntegerField(
        null=True,
        blank=True,
        help_text='Time estimate in hours'
    )

    # Dates
    due_date = models.DateField(
        null=True,
        blank=True,
        help_text='Issue due date'
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Issue started timestamp'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Issue completed timestamp'
    )
    cancelled_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Issue cancelled timestamp'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Issue creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'issues'
        verbose_name = 'Issue'
        verbose_name_plural = 'Issues'
        ordering = ['sort_order', '-created_at']
        unique_together = [['workspace', 'identifier']]
        indexes = [
            models.Index(fields=['workspace', 'status']),
            models.Index(fields=['project', 'status']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['identifier']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'sort_order']),
        ]

    def __str__(self):
        return f"{self.identifier} - {self.title}"

    def save(self, *args, **kwargs):
        """Auto-generate identifier if not set."""
        if not self.identifier:
            # Get project prefix
            prefix = self.project.identifier
            # Get next number for this project
            last_issue = Issue.objects.filter(
                project=self.project
            ).order_by('-id').first()

            if last_issue and last_issue.identifier:
                # Extract number from last identifier
                try:
                    last_num = int(last_issue.identifier.split('-')[-1])
                    next_num = last_num + 1
                except (ValueError, IndexError):
                    next_num = 1
            else:
                next_num = 1

            self.identifier = f"{prefix}-{next_num}"

        super().save(*args, **kwargs)


class IssueComment(models.Model):
    """
    Comment model for issue discussions.
    Supports markdown and mentions.
    """

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text='Associated issue'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issue_comments',
        help_text='Comment author'
    )
    content = models.TextField(
        help_text='Comment content (supports markdown)'
    )
    is_edited = models.BooleanField(
        default=False,
        help_text='Comment has been edited'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Comment creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'issue_comments'
        verbose_name = 'Issue Comment'
        verbose_name_plural = 'Issue Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['issue', 'created_at']),
            models.Index(fields=['author']),
        ]

    def __str__(self):
        return f"Comment on {self.issue.identifier} by {self.author.email}"


class IssueAttachment(models.Model):
    """
    Attachment model for files attached to issues.
    """

    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text='Associated issue'
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='issue_attachments',
        help_text='User who uploaded'
    )
    file_name = models.CharField(
        max_length=255,
        help_text='Original file name'
    )
    file_url = models.URLField(
        max_length=1000,
        help_text='URL to file (S3/storage)'
    )
    file_size = models.IntegerField(
        help_text='File size in bytes'
    )
    file_type = models.CharField(
        max_length=100,
        help_text='File MIME type'
    )

    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Upload timestamp'
    )

    class Meta:
        db_table = 'issue_attachments'
        verbose_name = 'Issue Attachment'
        verbose_name_plural = 'Issue Attachments'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['issue']),
            models.Index(fields=['uploaded_by']),
        ]

    def __str__(self):
        return f"{self.file_name} on {self.issue.identifier}"

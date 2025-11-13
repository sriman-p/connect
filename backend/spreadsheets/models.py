"""
Spreadsheets Models
Excel-like spreadsheet with real-time collaboration
"""

from django.db import models
from django.utils.text import slugify
from users.models import User
from workspaces.models import Workspace
from projects.models import Project


class Spreadsheet(models.Model):
    """Collaborative spreadsheet (Excel-like)."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='spreadsheets'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='spreadsheets'
    )

    # Spreadsheet details
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)

    # Owner and collaborators
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_spreadsheets'
    )

    editors = models.ManyToManyField(
        User,
        through='SpreadsheetEditor',
        related_name='editable_spreadsheets'
    )

    # Status
    is_template = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    # Permissions
    permission_level = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('team', 'Team'),
            ('workspace', 'Workspace'),
            ('public', 'Public'),
        ],
        default='team'
    )

    # Version control
    version = models.IntegerField(default=1)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='last_edited_spreadsheets'
    )

    # Metadata
    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['workspace', 'is_archived']),
            models.Index(fields=['created_by', 'updated_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Spreadsheet.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class SpreadsheetEditor(models.Model):
    """Spreadsheet editor permissions."""

    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('commenter', 'Commenter'),
        ('editor', 'Editor'),
        ('owner', 'Owner'),
    ]

    spreadsheet = models.ForeignKey(Spreadsheet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['spreadsheet', 'user']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class Sheet(models.Model):
    """Individual sheet within a spreadsheet."""

    spreadsheet = models.ForeignKey(
        Spreadsheet,
        on_delete=models.CASCADE,
        related_name='sheets'
    )

    # Sheet details
    name = models.CharField(max_length=100)
    position = models.IntegerField(default=0)

    # Sheet configuration
    row_count = models.IntegerField(default=100)
    column_count = models.IntegerField(default=26)

    # Frozen rows/columns
    frozen_rows = models.IntegerField(default=0)
    frozen_columns = models.IntegerField(default=0)

    # Grid lines and headings
    show_grid_lines = models.BooleanField(default=True)
    show_row_headings = models.BooleanField(default=True)
    show_column_headings = models.BooleanField(default=True)

    # Protected sheet
    is_protected = models.BooleanField(default=False)
    protection_password = models.CharField(max_length=128, blank=True)

    # Sheet color for tabs
    tab_color = models.CharField(max_length=7, default='#ffffff')

    # Visibility
    is_hidden = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position']
        unique_together = ['spreadsheet', 'name']

    def __str__(self):
        return f"{self.spreadsheet.title} - {self.name}"


class Cell(models.Model):
    """Individual cell in a sheet."""

    sheet = models.ForeignKey(
        Sheet,
        on_delete=models.CASCADE,
        related_name='cells'
    )

    # Cell position
    row = models.IntegerField()
    column = models.IntegerField()

    # Cell content
    value = models.TextField(blank=True)  # Raw value
    formula = models.TextField(blank=True)  # Formula (if applicable)
    computed_value = models.TextField(blank=True)  # Computed result

    # Data type
    data_type = models.CharField(
        max_length=20,
        choices=[
            ('text', 'Text'),
            ('number', 'Number'),
            ('boolean', 'Boolean'),
            ('date', 'Date'),
            ('time', 'Time'),
            ('datetime', 'DateTime'),
            ('currency', 'Currency'),
            ('percentage', 'Percentage'),
            ('formula', 'Formula'),
        ],
        default='text'
    )

    # Formatting
    format_config = models.JSONField(default=dict)  # {bold, italic, color, background, etc.}

    # Validation
    validation_config = models.JSONField(null=True, blank=True)  # Data validation rules

    # Cell metadata
    note = models.TextField(blank=True)  # Cell note/comment
    hyperlink = models.URLField(blank=True)

    # Merging
    merge_config = models.JSONField(null=True, blank=True)  # {rows, columns} for merged cells

    # Locked (for protected sheets)
    is_locked = models.BooleanField(default=False)

    # Version tracking
    version = models.IntegerField(default=1)
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='modified_cells'
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['sheet', 'row', 'column']
        indexes = [
            models.Index(fields=['sheet', 'row', 'column']),
            models.Index(fields=['sheet', 'updated_at']),
        ]

    def __str__(self):
        # Convert column number to letter (0 -> A, 1 -> B, etc.)
        column_letter = self._column_to_letter(self.column)
        return f"{self.sheet.name}!{column_letter}{self.row + 1}"

    @staticmethod
    def _column_to_letter(column):
        """Convert column number to Excel-style letter."""
        result = ""
        while column >= 0:
            result = chr(column % 26 + 65) + result
            column = column // 26 - 1
        return result


class NamedRange(models.Model):
    """Named range in a spreadsheet."""

    spreadsheet = models.ForeignKey(
        Spreadsheet,
        on_delete=models.CASCADE,
        related_name='named_ranges'
    )

    name = models.CharField(max_length=100)

    # Range definition
    sheet = models.ForeignKey(Sheet, on_delete=models.CASCADE)
    start_row = models.IntegerField()
    start_column = models.IntegerField()
    end_row = models.IntegerField()
    end_column = models.IntegerField()

    # Metadata
    description = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['spreadsheet', 'name']

    def __str__(self):
        return f"{self.spreadsheet.title} - {self.name}"


class SpreadsheetSession(models.Model):
    """Active editing session for real-time collaboration."""

    spreadsheet = models.ForeignKey(
        Spreadsheet,
        on_delete=models.CASCADE,
        related_name='active_sessions'
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Session tracking
    session_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    # Current cell/range selection
    selected_cell = models.JSONField(null=True, blank=True)  # {sheet, row, column}
    selected_range = models.JSONField(null=True, blank=True)  # {sheet, startRow, startCol, endRow, endCol}

    # User color for selection display
    user_color = models.CharField(max_length=7)  # Hex color

    # Current sheet
    active_sheet = models.ForeignKey(
        Sheet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Metadata
    joined_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_activity_at']
        indexes = [
            models.Index(fields=['spreadsheet', 'is_active']),
        ]

    def __str__(self):
        return f"{self.user.email} editing {self.spreadsheet.title}"


class SpreadsheetOperation(models.Model):
    """Operational transformation log for real-time collaboration."""

    spreadsheet = models.ForeignKey(
        Spreadsheet,
        on_delete=models.CASCADE,
        related_name='operations'
    )

    session = models.ForeignKey(
        SpreadsheetSession,
        on_delete=models.CASCADE,
        related_name='operations'
    )

    # Operation details
    operation_type = models.CharField(
        max_length=20,
        choices=[
            ('cell_update', 'Cell Update'),
            ('row_insert', 'Row Insert'),
            ('row_delete', 'Row Delete'),
            ('column_insert', 'Column Insert'),
            ('column_delete', 'Column Delete'),
            ('format_update', 'Format Update'),
            ('merge_cells', 'Merge Cells'),
            ('unmerge_cells', 'Unmerge Cells'),
        ]
    )

    # Operation data
    operation_data = models.JSONField()  # {sheet, row, column, value, etc.}

    # Version control
    base_version = models.IntegerField()
    sequence_number = models.IntegerField()

    # Acknowledgment
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'sequence_number']
        indexes = [
            models.Index(fields=['spreadsheet', 'created_at']),
            models.Index(fields=['session', 'sequence_number']),
        ]

    def __str__(self):
        return f"{self.operation_type} by {self.session.user.email}"


class Chart(models.Model):
    """Chart in a spreadsheet."""

    sheet = models.ForeignKey(
        Sheet,
        on_delete=models.CASCADE,
        related_name='charts'
    )

    # Chart details
    title = models.CharField(max_length=200)

    chart_type = models.CharField(
        max_length=20,
        choices=[
            ('line', 'Line'),
            ('bar', 'Bar'),
            ('column', 'Column'),
            ('pie', 'Pie'),
            ('area', 'Area'),
            ('scatter', 'Scatter'),
            ('radar', 'Radar'),
            ('bubble', 'Bubble'),
        ]
    )

    # Data range
    data_range = models.JSONField()  # {sheet, startRow, startCol, endRow, endCol}

    # Chart configuration
    config = models.JSONField(default=dict)  # Colors, legend, axes, etc.

    # Position on sheet
    position = models.JSONField()  # {row, column, width, height}

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} ({self.chart_type})"


class SpreadsheetComment(models.Model):
    """Comment on a cell or range."""

    sheet = models.ForeignKey(
        Sheet,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    # Position (cell or range)
    row = models.IntegerField()
    column = models.IntegerField()

    # Thread
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Status
    is_resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_spreadsheet_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email}"

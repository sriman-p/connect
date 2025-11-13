"""
Files Models
File storage and sharing (Google Drive-like)
"""

from django.db import models
from django.core.validators import FileExtensionValidator
from users.models import User
from workspaces.models import Workspace
from projects.models import Project


class File(models.Model):
    """Uploaded file."""

    FILE_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('spreadsheet', 'Spreadsheet'),
        ('presentation', 'Presentation'),
        ('pdf', 'PDF'),
        ('archive', 'Archive'),
        ('code', 'Code'),
        ('other', 'Other'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='files'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files'
    )

    # File details
    name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FILE_TYPE_CHOICES)
    mime_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField()  # Bytes

    # Storage
    file_url = models.URLField()  # S3/Cloud storage URL
    file_path = models.CharField(max_length=500)  # Storage path

    # Previews
    thumbnail_url = models.URLField(blank=True)
    preview_url = models.URLField(blank=True)  # For documents/images

    # Owner and permissions
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files'
    )

    shared_with = models.ManyToManyField(
        User,
        through='FileShare',
        related_name='shared_files'
    )

    # Folder organization
    folder = models.ForeignKey(
        'FileFolder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='files'
    )

    # Status
    is_public = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)

    # Virus scan
    is_scanned = models.BooleanField(default=False)
    scan_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('clean', 'Clean'),
            ('infected', 'Infected'),
        ],
        default='pending'
    )

    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)

    # File metadata (EXIF, etc.)
    metadata = models.JSONField(default=dict, blank=True)

    # Download tracking
    download_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['workspace', 'is_archived']),
            models.Index(fields=['uploaded_by', 'uploaded_at']),
            models.Index(fields=['file_type']),
            models.Index(fields=['folder']),
        ]

    def __str__(self):
        return self.name

    def get_file_extension(self):
        """Get file extension."""
        return self.name.split('.')[-1] if '.' in self.name else ''


class FileShare(models.Model):
    """File sharing permissions."""

    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('comment', 'Comment'),
        ('edit', 'Edit'),
        ('owner', 'Owner'),
    ]

    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    permission = models.CharField(max_length=20, choices=PERMISSION_CHOICES)

    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    shared_at = models.DateTimeField(auto_now_add=True)
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='file_shares_given'
    )

    class Meta:
        unique_together = ['file', 'user']
        ordering = ['-shared_at']

    def __str__(self):
        return f"{self.file.name} - {self.user.email}"


class FileFolder(models.Model):
    """Folder for organizing files."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='file_folders'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Nested folders
    parent_folder = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfolders'
    )

    # Owner
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    # Color for UI
    color = models.CharField(max_length=7, default='#3b82f6')

    # Permissions
    is_shared = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['workspace', 'parent_folder', 'name']

    def __str__(self):
        return self.name


class FileVersion(models.Model):
    """File version history."""

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version_number = models.IntegerField()

    # Version file storage
    file_url = models.URLField()
    file_size = models.BigIntegerField()

    # Changes
    change_summary = models.TextField(blank=True)

    # Uploader
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['file', 'version_number']

    def __str__(self):
        return f"{self.file.name} - v{self.version_number}"


class FileComment(models.Model):
    """Comment on a file."""

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    # Thread
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email}"


class SharedLink(models.Model):
    """Public/private shareable link for files."""

    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='shared_links'
    )

    # Link details
    link_id = models.CharField(max_length=32, unique=True)  # UUID
    password = models.CharField(max_length=128, blank=True)  # Hashed

    # Permissions
    permission = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View Only'),
            ('download', 'Download'),
            ('edit', 'Edit'),
        ],
        default='view'
    )

    # Limits
    max_downloads = models.IntegerField(null=True, blank=True)
    download_count = models.IntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)

    # Creator
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Link for {self.file.name}"

    def get_share_url(self):
        """Get the full shareable URL."""
        return f"/share/{self.link_id}"

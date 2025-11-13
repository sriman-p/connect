"""
Documents Models
Collaborative document editing (Google Docs-like)
"""

from django.db import models
from django.utils.text import slugify
from users.models import User
from workspaces.models import Workspace
from projects.models import Project


class Document(models.Model):
    """Collaborative document."""

    DOC_TYPE_CHOICES = [
        ('doc', 'Document'),
        ('sheet', 'Spreadsheet'),
        ('slide', 'Presentation'),
        ('form', 'Form'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    # Document details
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)

    # Content (stored as JSON for collaborative editing)
    content = models.JSONField(default=dict)  # Tiptap/ProseMirror format
    plain_text = models.TextField(blank=True)  # For search indexing

    # Owner and collaborators
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_documents'
    )

    editors = models.ManyToManyField(
        User,
        through='DocumentEditor',
        related_name='editable_documents'
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
        related_name='last_edited_documents'
    )

    # Folder organization
    folder = models.ForeignKey(
        'DocumentFolder',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents'
    )

    # Metadata
    word_count = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['workspace', 'is_archived']),
            models.Index(fields=['created_by', 'updated_at']),
            models.Index(fields=['folder', 'title']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Ensure uniqueness
            original_slug = self.slug
            counter = 1
            while Document.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)


class DocumentEditor(models.Model):
    """Document editor permissions."""

    ROLE_CHOICES = [
        ('viewer', 'Viewer'),
        ('commenter', 'Commenter'),
        ('editor', 'Editor'),
        ('owner', 'Owner'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Metadata
    added_at = models.DateTimeField(auto_now_add=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['document', 'user']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class DocumentVersion(models.Model):
    """Document version history."""

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )

    version_number = models.IntegerField()
    content = models.JSONField()  # Snapshot of content

    # Changes
    changes_summary = models.TextField(blank=True)

    # Author
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ['document', 'version_number']

    def __str__(self):
        return f"{self.document.title} - v{self.version_number}"


class DocumentComment(models.Model):
    """Comment on a document."""

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    # Position in document (for inline comments)
    position = models.JSONField(null=True, blank=True)  # {start, end, block}

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
        related_name='resolved_comments'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.email}"


class DocumentFolder(models.Model):
    """Folder for organizing documents."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='document_folders'
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

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['workspace', 'parent_folder', 'name']

    def __str__(self):
        return self.name


class DocumentTemplate(models.Model):
    """Document template."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='document_templates'
    )

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    doc_type = models.CharField(max_length=20, choices=Document.DOC_TYPE_CHOICES)

    # Template content
    content = models.JSONField()

    # Metadata
    thumbnail_url = models.URLField(blank=True)
    is_public = models.BooleanField(default=False)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

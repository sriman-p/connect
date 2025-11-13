"""
Knowledge Base Models
Wiki, documentation, and knowledge management
"""

from django.db import models
from django.utils.text import slugify
from users.models import User
from workspaces.models import Workspace


class WikiPage(models.Model):
    """Wiki page / knowledge article."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='wiki_pages'
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220)
    content = models.TextField()  # Markdown or HTML
    excerpt = models.TextField(blank=True, max_length=500)

    # Parent page for hierarchy
    parent_page = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_pages'
    )

    # Category
    category = models.ForeignKey(
        'WikiCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pages'
    )

    # Authors
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_wiki_pages'
    )
    contributors = models.ManyToManyField(
        User,
        through='WikiContribution',
        related_name='contributed_wiki_pages'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived'),
        ],
        default='draft'
    )

    # Permissions
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('team', 'Team'),
            ('workspace', 'Workspace'),
            ('public', 'Public'),
        ],
        default='workspace'
    )

    # Featured
    is_featured = models.BooleanField(default=False)

    # SEO and metadata
    tags = models.JSONField(default=list, blank=True)
    view_count = models.IntegerField(default=0)

    # Version control
    version = models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ['workspace', 'slug']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class WikiCategory(models.Model):
    """Wiki category."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='wiki_categories'
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=110)
    description = models.TextField(blank=True)

    # Icon and color
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#3b82f6')

    # Order
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['workspace', 'slug']
        verbose_name_plural = 'Wiki categories'

    def __str__(self):
        return self.name


class WikiContribution(models.Model):
    """Wiki page contribution."""

    page = models.ForeignKey(WikiPage, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    contribution_type = models.CharField(
        max_length=20,
        choices=[
            ('created', 'Created'),
            ('edited', 'Edited'),
            ('reviewed', 'Reviewed'),
        ]
    )

    contributed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-contributed_at']

    def __str__(self):
        return f"{self.user.email} - {self.page.title}"


class FAQ(models.Model):
    """Frequently Asked Question."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='faqs'
    )

    question = models.CharField(max_length=300)
    answer = models.TextField()

    # Category
    category = models.CharField(max_length=100, blank=True)

    # Metadata
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    order = models.IntegerField(default=0)

    # Visibility
    is_published = models.BooleanField(default=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-helpful_count']
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQs'

    def __str__(self):
        return self.question

"""
Search Models
Advanced search with indexing and history
"""

from django.db import models
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from users.models import User
from workspaces.models import Workspace


class SearchIndex(models.Model):
    """Global search index."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='search_indexes'
    )

    # Content
    title = models.CharField(max_length=500)
    content = models.TextField()
    excerpt = models.TextField(blank=True)

    # Source
    content_type = models.CharField(max_length=50)  # issue, document, file, etc.
    object_id = models.CharField(max_length=100)
    url = models.CharField(max_length=500)

    # Metadata
    tags = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    # Creator
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Search vector for full-text search
    search_vector = SearchVectorField(null=True)

    # Boost score (for relevance ranking)
    boost_score = models.FloatField(default=1.0)

    indexed_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['workspace', 'content_type']),
        ]
        unique_together = ['workspace', 'content_type', 'object_id']

    def __str__(self):
        return self.title


class SearchQuery(models.Model):
    """Search query history and analytics."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='search_queries'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='search_queries'
    )

    query = models.CharField(max_length=500)

    # Filters applied
    filters = models.JSONField(default=dict, blank=True)

    # Results
    result_count = models.IntegerField(default=0)

    # Did user click a result?
    clicked_result = models.BooleanField(default=False)
    clicked_result_id = models.CharField(max_length=100, blank=True)

    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']
        verbose_name_plural = 'Search queries'

    def __str__(self):
        return self.query


class SavedSearch(models.Model):
    """User saved search."""

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )

    name = models.CharField(max_length=100)
    query = models.CharField(max_length=500)
    filters = models.JSONField(default=dict)

    # Notifications
    notify_on_new_results = models.BooleanField(default=False)

    is_pinned = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', 'name']

    def __str__(self):
        return self.name

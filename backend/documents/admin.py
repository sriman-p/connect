"""
Documents Admin Interface
"""

from django.contrib import admin
from .models import (
    Document, DocumentEditor, DocumentVersion, DocumentComment,
    DocumentFolder, DocumentTemplate, DocumentSession, DocumentOperation
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin interface for documents."""

    list_display = [
        'title', 'doc_type', 'workspace', 'created_by',
        'is_archived', 'is_published', 'permission_level',
        'version', 'word_count', 'updated_at'
    ]
    list_filter = [
        'doc_type', 'is_archived', 'is_published',
        'permission_level', 'created_at'
    ]
    search_fields = ['title', 'plain_text', 'slug']
    readonly_fields = [
        'slug', 'version', 'word_count', 'view_count',
        'created_at', 'updated_at'
    ]
    raw_id_fields = ['workspace', 'project', 'created_by', 'last_edited_by', 'folder']
    date_hierarchy = 'created_at'
    ordering = ['-updated_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'doc_type', 'workspace', 'project')
        }),
        ('Content', {
            'fields': ('content', 'plain_text', 'word_count')
        }),
        ('Ownership', {
            'fields': ('created_by', 'last_edited_by')
        }),
        ('Organization', {
            'fields': ('folder', 'is_template')
        }),
        ('Status', {
            'fields': ('is_archived', 'is_published', 'published_at', 'permission_level')
        }),
        ('Metadata', {
            'fields': ('version', 'view_count', 'created_at', 'updated_at')
        }),
    )


@admin.register(DocumentEditor)
class DocumentEditorAdmin(admin.ModelAdmin):
    """Admin interface for document editors."""

    list_display = ['document', 'user', 'role', 'added_at', 'last_viewed_at']
    list_filter = ['role', 'added_at']
    search_fields = ['document__title', 'user__email']
    raw_id_fields = ['document', 'user']
    date_hierarchy = 'added_at'


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    """Admin interface for document versions."""

    list_display = ['document', 'version_number', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['document__title', 'changes_summary']
    raw_id_fields = ['document', 'created_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    """Admin interface for document comments."""

    list_display = [
        'document', 'author', 'content_preview',
        'is_resolved', 'created_at'
    ]
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['document__title', 'author__email', 'content']
    raw_id_fields = ['document', 'author', 'parent_comment', 'resolved_by']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        """Show preview of comment content."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(DocumentFolder)
class DocumentFolderAdmin(admin.ModelAdmin):
    """Admin interface for document folders."""

    list_display = ['name', 'workspace', 'parent_folder', 'created_by', 'color', 'created_at']
    list_filter = ['workspace', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['workspace', 'parent_folder', 'created_by']
    date_hierarchy = 'created_at'


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    """Admin interface for document templates."""

    list_display = ['name', 'doc_type', 'workspace', 'is_public', 'created_by', 'created_at']
    list_filter = ['doc_type', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['workspace', 'created_by']
    date_hierarchy = 'created_at'


@admin.register(DocumentSession)
class DocumentSessionAdmin(admin.ModelAdmin):
    """Admin interface for document sessions."""

    list_display = [
        'document', 'user', 'session_id',
        'is_active', 'user_color', 'joined_at', 'last_activity_at'
    ]
    list_filter = ['is_active', 'joined_at']
    search_fields = ['document__title', 'user__email', 'session_id']
    raw_id_fields = ['document', 'user']
    date_hierarchy = 'joined_at'
    readonly_fields = ['session_id', 'joined_at', 'last_activity_at']


@admin.register(DocumentOperation)
class DocumentOperationAdmin(admin.ModelAdmin):
    """Admin interface for document operations."""

    list_display = [
        'document', 'operation_type', 'base_version',
        'sequence_number', 'is_acknowledged', 'created_at'
    ]
    list_filter = ['operation_type', 'is_acknowledged', 'created_at']
    search_fields = ['document__title']
    raw_id_fields = ['document', 'session']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

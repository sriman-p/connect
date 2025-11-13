from django.contrib import admin
from .models import Label, Issue, IssueComment, IssueAttachment


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    """Admin interface for Label model."""

    list_display = ['name', 'workspace', 'color', 'created_at']
    list_filter = ['workspace', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']


class IssueCommentInline(admin.TabularInline):
    """Inline admin for issue comments."""
    model = IssueComment
    extra = 0
    fields = ['author', 'content', 'is_edited', 'created_at']
    readonly_fields = ['author', 'is_edited', 'created_at']


class IssueAttachmentInline(admin.TabularInline):
    """Inline admin for issue attachments."""
    model = IssueAttachment
    extra = 0
    fields = ['file_name', 'file_url', 'file_size', 'uploaded_by', 'uploaded_at']
    readonly_fields = ['uploaded_by', 'uploaded_at']


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    """Admin interface for Issue model."""

    list_display = [
        'identifier',
        'title',
        'project',
        'status',
        'priority',
        'assignee',
        'created_at',
    ]
    list_filter = [
        'status',
        'priority',
        'issue_type',
        'project',
        'created_at',
    ]
    search_fields = ['identifier', 'title', 'description']
    readonly_fields = [
        'identifier',
        'reporter',
        'started_at',
        'completed_at',
        'cancelled_at',
        'created_at',
        'updated_at',
    ]
    filter_horizontal = ['labels']
    inlines = [IssueCommentInline, IssueAttachmentInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'project', 'identifier', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('issue_type', 'priority', 'status', 'labels')
        }),
        ('Assignment', {
            'fields': ('assignee', 'reporter')
        }),
        ('Hierarchy', {
            'fields': ('parent', 'sort_order')
        }),
        ('Planning', {
            'fields': ('estimate', 'due_date')
        }),
        ('Tracking', {
            'fields': ('started_at', 'completed_at', 'cancelled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(IssueComment)
class IssueCommentAdmin(admin.ModelAdmin):
    """Admin interface for IssueComment model."""

    list_display = ['issue', 'author', 'is_edited', 'created_at']
    list_filter = ['is_edited', 'created_at']
    search_fields = ['content', 'issue__identifier', 'author__email']
    readonly_fields = ['author', 'is_edited', 'created_at', 'updated_at']

    fieldsets = (
        ('Comment', {
            'fields': ('issue', 'author', 'content')
        }),
        ('Metadata', {
            'fields': ('is_edited', 'created_at', 'updated_at')
        }),
    )


@admin.register(IssueAttachment)
class IssueAttachmentAdmin(admin.ModelAdmin):
    """Admin interface for IssueAttachment model."""

    list_display = [
        'file_name',
        'issue',
        'uploaded_by',
        'file_size',
        'uploaded_at',
    ]
    list_filter = ['uploaded_at']
    search_fields = ['file_name', 'issue__identifier', 'uploaded_by__email']
    readonly_fields = ['uploaded_by', 'uploaded_at']

    fieldsets = (
        ('File Information', {
            'fields': ('issue', 'file_name', 'file_url', 'file_size', 'file_type')
        }),
        ('Metadata', {
            'fields': ('uploaded_by', 'uploaded_at')
        }),
    )

"""
Files Admin Interface
"""

from django.contrib import admin
from .models import File, FileFolder, FileShare, FileVersion


class FileShareInline(admin.TabularInline):
    """Inline admin for file shares."""
    model = FileShare
    extra = 0
    fields = ['user', 'permission_level', 'shared_at']
    readonly_fields = ['shared_at']


class FileVersionInline(admin.TabularInline):
    """Inline admin for file versions."""
    model = FileVersion
    extra = 0
    fields = ['version_number', 'file_size', 'uploaded_by', 'created_at']
    readonly_fields = ['created_at']
    ordering = ['-version_number']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """Admin interface for files."""

    list_display = [
        'name', 'file_type', 'file_size_mb', 'uploaded_by',
        'workspace', 'is_public', 'scan_status', 'uploaded_at'
    ]
    list_filter = [
        'file_type', 'is_public', 'is_archived',
        'is_starred', 'scan_status', 'uploaded_at'
    ]
    search_fields = ['name', 'description', 'uploaded_by__email']
    readonly_fields = [
        'file_size', 'mime_type', 'uploaded_at',
        'updated_at', 'download_count', 'file_size_mb'
    ]
    inlines = [FileShareInline, FileVersionInline]
    date_hierarchy = 'uploaded_at'

    fieldsets = (
        ('File Information', {
            'fields': (
                'workspace', 'project', 'folder',
                'name', 'description', 'tags'
            )
        }),
        ('File Details', {
            'fields': (
                'file_type', 'mime_type', 'file_size',
                'file_size_mb', 'file_url', 'file_path'
            )
        }),
        ('Previews', {
            'fields': ('thumbnail_url', 'preview_url'),
            'classes': ('collapse',),
        }),
        ('Owner & Sharing', {
            'fields': ('uploaded_by', 'is_public')
        }),
        ('Status', {
            'fields': (
                'is_archived', 'is_starred',
                'is_scanned', 'scan_status'
            )
        }),
        ('Metadata', {
            'fields': (
                'download_count', 'uploaded_at', 'updated_at'
            )
        }),
    )

    def file_size_mb(self, obj):
        """Show file size in MB."""
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "-"
    file_size_mb.short_description = 'File Size (MB)'


@admin.register(FileFolder)
class FileFolderAdmin(admin.ModelAdmin):
    """Admin interface for file folders."""

    list_display = [
        'name', 'workspace', 'parent', 'created_by',
        'is_public', 'created_at'
    ]
    list_filter = ['is_public', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['parent']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Folder Information', {
            'fields': ('workspace', 'parent', 'name', 'description')
        }),
        ('Settings', {
            'fields': ('created_by', 'is_public', 'color')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(FileShare)
class FileShareAdmin(admin.ModelAdmin):
    """Admin interface for file shares."""

    list_display = [
        'file', 'user', 'shared_by', 'permission_level',
        'shared_at', 'expires_at'
    ]
    list_filter = ['permission_level', 'shared_at']
    search_fields = ['file__name', 'user__email', 'shared_by__email']
    readonly_fields = ['shared_at']
    date_hierarchy = 'shared_at'

    fieldsets = (
        ('Share Information', {
            'fields': ('file', 'user', 'shared_by')
        }),
        ('Permissions', {
            'fields': ('permission_level', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('shared_at',)
        }),
    )


@admin.register(FileVersion)
class FileVersionAdmin(admin.ModelAdmin):
    """Admin interface for file versions."""

    list_display = [
        'file', 'version_number', 'file_size_mb',
        'uploaded_by', 'comment', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['file__name', 'uploaded_by__email', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Version Information', {
            'fields': (
                'file', 'version_number', 'comment'
            )
        }),
        ('File Details', {
            'fields': (
                'file_url', 'file_size', 'uploaded_by'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

    def file_size_mb(self, obj):
        """Show file size in MB."""
        if obj.file_size:
            return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "-"
    file_size_mb.short_description = 'File Size (MB)'

from django.contrib import admin
from .models import Project, ProjectMember


class ProjectMemberInline(admin.TabularInline):
    """Inline admin for project members."""
    model = ProjectMember
    extra = 0
    fields = ['user', 'added_at']
    readonly_fields = ['added_at']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Admin interface for Project model."""

    list_display = [
        'identifier',
        'name',
        'workspace',
        'status',
        'lead',
        'progress',
        'is_archived',
        'created_at',
    ]
    list_filter = ['status', 'is_archived', 'workspace', 'created_at']
    search_fields = ['name', 'identifier', 'description']
    readonly_fields = [
        'created_at',
        'updated_at',
        'completed_at',
        'issue_count',
        'completed_issue_count',
        'progress',
    ]
    inlines = [ProjectMemberInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'name', 'identifier', 'description')
        }),
        ('Status & Timeline', {
            'fields': ('status', 'start_date', 'target_date', 'completed_at')
        }),
        ('Team', {
            'fields': ('lead', 'created_by')
        }),
        ('Settings', {
            'fields': ('color', 'icon', 'is_archived', 'is_private')
        }),
        ('Metrics', {
            'fields': ('issue_count', 'completed_issue_count', 'progress')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    """Admin interface for ProjectMember model."""

    list_display = ['user', 'project', 'added_at']
    list_filter = ['project', 'added_at']
    search_fields = ['user__email', 'project__name']
    readonly_fields = ['added_at']

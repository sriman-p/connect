from django.contrib import admin
from .models import Workspace, WorkspaceMember


class WorkspaceMemberInline(admin.TabularInline):
    """Inline admin for workspace members."""
    model = WorkspaceMember
    extra = 0
    fields = ['user', 'role', 'permissions', 'is_active', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    """Admin interface for Workspace model."""

    list_display = ['name', 'slug', 'owner', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WorkspaceMemberInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'owner')
        }),
        ('Settings', {
            'fields': ('logo_url', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    """Admin interface for WorkspaceMember model."""

    list_display = ['user', 'workspace', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__email', 'workspace__name']
    readonly_fields = ['joined_at', 'updated_at']

    fieldsets = (
        ('Membership', {
            'fields': ('workspace', 'user', 'role')
        }),
        ('Permissions', {
            'fields': ('permissions', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'updated_at')
        }),
    )

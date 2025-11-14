"""
Approvals Admin Interface
"""

from django.contrib import admin
from .models import ApprovalWorkflow, ApprovalStep, ApprovalRequest, ApprovalAction


class ApprovalStepInline(admin.TabularInline):
    """Inline admin for approval steps."""
    model = ApprovalStep
    extra = 0
    fields = ['name', 'order', 'required_approvals', 'allow_delegation']
    ordering = ['order']


@admin.register(ApprovalWorkflow)
class ApprovalWorkflowAdmin(admin.ModelAdmin):
    """Admin interface for approval workflows."""

    list_display = [
        'name', 'workspace', 'workflow_type',
        'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['workflow_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ApprovalStepInline]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'name', 'description')
        }),
        ('Workflow Settings', {
            'fields': ('workflow_type', 'auto_approve_after_hours')
        }),
        ('Status', {
            'fields': ('is_active', 'created_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    """Admin interface for approval steps."""

    list_display = [
        'workflow', 'name', 'order',
        'required_approvals', 'allow_delegation'
    ]
    list_filter = ['workflow', 'allow_delegation']
    search_fields = ['name', 'description', 'workflow__name']
    filter_horizontal = ['approvers']

    fieldsets = (
        ('Step Information', {
            'fields': ('workflow', 'name', 'description', 'order')
        }),
        ('Approvers', {
            'fields': ('approvers', 'required_approvals')
        }),
        ('Settings', {
            'fields': ('allow_delegation',)
        }),
    )


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    """Admin interface for approval requests."""

    list_display = [
        'title', 'workflow', 'status', 'priority',
        'requester', 'created_at', 'due_date'
    ]
    list_filter = ['status', 'priority', 'workflow', 'created_at']
    search_fields = ['title', 'description', 'requester__email']
    readonly_fields = [
        'created_at', 'updated_at', 'submitted_at',
        'approved_at', 'rejected_at'
    ]
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Request Information', {
            'fields': ('workflow', 'title', 'description', 'priority')
        }),
        ('Requester', {
            'fields': ('workspace', 'requester')
        }),
        ('Status', {
            'fields': ('status', 'due_date')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': (
                'created_at', 'updated_at', 'submitted_at',
                'approved_at', 'rejected_at'
            )
        }),
    )


@admin.register(ApprovalAction)
class ApprovalActionAdmin(admin.ModelAdmin):
    """Admin interface for approval actions."""

    list_display = [
        'approval_request', 'approver', 'action',
        'step', 'created_at'
    ]
    list_filter = ['action', 'created_at']
    search_fields = [
        'approval_request__title', 'approver__email',
        'comments'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Action Information', {
            'fields': ('approval_request', 'step', 'approver')
        }),
        ('Decision', {
            'fields': ('action', 'comments')
        }),
        ('Delegation', {
            'fields': ('delegated_to',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )

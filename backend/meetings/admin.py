"""
Meetings Admin Interface
"""

from django.contrib import admin
from .models import Meeting, MeetingParticipant, MeetingNote, MeetingRecording


class MeetingParticipantInline(admin.TabularInline):
    """Inline admin for meeting participants."""
    model = MeetingParticipant
    extra = 0
    fields = ['user', 'role', 'status', 'joined_at', 'left_at']
    readonly_fields = ['joined_at', 'left_at']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    """Admin interface for meetings."""

    list_display = [
        'title', 'workspace', 'organizer', 'meeting_type',
        'status', 'start_time', 'duration_minutes', 'is_recorded'
    ]
    list_filter = [
        'meeting_type', 'status', 'is_recurring',
        'is_recorded', 'start_time'
    ]
    search_fields = ['title', 'description', 'meeting_id']
    readonly_fields = [
        'meeting_id', 'created_at', 'updated_at',
        'started_at', 'ended_at', 'duration_minutes'
    ]
    inlines = [MeetingParticipantInline]
    date_hierarchy = 'start_time'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'title', 'description', 'meeting_type', 'status')
        }),
        ('Scheduling', {
            'fields': ('start_time', 'end_time', 'timezone')
        }),
        ('Recurring Settings', {
            'fields': ('is_recurring', 'recurrence_rule', 'recurrence_end_date'),
            'classes': ('collapse',),
        }),
        ('Organizer', {
            'fields': ('organizer',)
        }),
        ('Meeting Room', {
            'fields': ('meeting_url', 'meeting_id', 'meeting_password')
        }),
        ('Settings', {
            'fields': ('is_recorded', 'recording_url', 'allow_guests', 'require_approval')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'started_at', 'ended_at', 'duration_minutes')
        }),
    )


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    """Admin interface for meeting participants."""

    list_display = [
        'user', 'meeting', 'role', 'status',
        'joined_at', 'left_at'
    ]
    list_filter = ['role', 'status', 'joined_at']
    search_fields = ['user__email', 'meeting__title']
    readonly_fields = ['joined_at', 'left_at']
    date_hierarchy = 'joined_at'


@admin.register(MeetingNote)
class MeetingNoteAdmin(admin.ModelAdmin):
    """Admin interface for meeting notes."""

    list_display = [
        'meeting', 'created_by', 'title',
        'is_shared', 'created_at'
    ]
    list_filter = ['is_shared', 'created_at']
    search_fields = ['title', 'content', 'meeting__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Note Information', {
            'fields': ('meeting', 'title', 'content')
        }),
        ('Settings', {
            'fields': ('created_by', 'is_shared')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(MeetingRecording)
class MeetingRecordingAdmin(admin.ModelAdmin):
    """Admin interface for meeting recordings."""

    list_display = [
        'meeting', 'recording_url', 'duration_seconds',
        'file_size_mb', 'created_at'
    ]
    list_filter = ['created_at']
    search_fields = ['meeting__title', 'recording_url']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Recording Information', {
            'fields': ('meeting', 'recording_url', 'duration_seconds', 'file_size')
        }),
        ('Transcript', {
            'fields': ('transcript_url',)
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
    file_size_mb.short_description = 'File Size'

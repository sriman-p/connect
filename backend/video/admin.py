"""
Video Conferencing Admin Interface
"""

from django.contrib import admin
from .models import VideoRoom, VideoParticipant, VideoRecording, VideoInvitation


@admin.register(VideoRoom)
class VideoRoomAdmin(admin.ModelAdmin):
    """Admin interface for video rooms."""

    list_display = [
        'name', 'workspace', 'host', 'provider', 'status',
        'peak_participants', 'scheduled_start', 'created_at'
    ]
    list_filter = ['provider', 'status', 'enable_recording', 'created_at']
    search_fields = ['name', 'room_id', 'workspace__name', 'host__email']
    readonly_fields = ['room_id', 'started_at', 'ended_at', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'room_id', 'name', 'description', 'host')
        }),
        ('Provider', {
            'fields': ('provider', 'provider_room_id', 'provider_data')
        }),
        ('Settings', {
            'fields': (
                'max_participants', 'require_password', 'password',
                'enable_recording', 'enable_screen_share', 'enable_chat'
            )
        }),
        ('Schedule', {
            'fields': ('scheduled_start', 'scheduled_end', 'status')
        }),
        ('Session Times', {
            'fields': ('started_at', 'ended_at')
        }),
        ('Statistics', {
            'fields': ('peak_participants', 'total_duration_minutes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(VideoParticipant)
class VideoParticipantAdmin(admin.ModelAdmin):
    """Admin interface for video participants."""

    list_display = [
        'get_participant_name', 'room', 'role', 'status',
        'audio_enabled', 'video_enabled', 'joined_at', 'left_at'
    ]
    list_filter = ['role', 'status', 'audio_enabled', 'video_enabled']
    search_fields = ['user__email', 'guest_name', 'room__name']
    readonly_fields = ['created_at', 'updated_at']

    def get_participant_name(self, obj):
        return obj.user.email if obj.user else obj.guest_name
    get_participant_name.short_description = 'Participant'


@admin.register(VideoRecording)
class VideoRecordingAdmin(admin.ModelAdmin):
    """Admin interface for video recordings."""

    list_display = [
        'title', 'room', 'status', 'duration_seconds',
        'file_size_mb', 'recorded_at', 'processed_at'
    ]
    list_filter = ['status', 'format', 'recorded_at']
    search_fields = ['title', 'room__name']
    readonly_fields = ['created_at', 'updated_at', 'processed_at']
    date_hierarchy = 'recorded_at'


@admin.register(VideoInvitation)
class VideoInvitationAdmin(admin.ModelAdmin):
    """Admin interface for video invitations."""

    list_display = [
        'get_invitee_email', 'room', 'inviter', 'status',
        'created_at', 'expires_at', 'responded_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['invitee__email', 'invitee_email', 'room__name']
    readonly_fields = ['token', 'created_at', 'responded_at']

    def get_invitee_email(self, obj):
        return obj.invitee.email if obj.invitee else obj.invitee_email
    get_invitee_email.short_description = 'Invitee'

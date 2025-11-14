"""
Video Conferencing Serializers
"""

from rest_framework import serializers
from .models import VideoRoom, VideoParticipant, VideoRecording, VideoInvitation


class VideoParticipantSerializer(serializers.ModelSerializer):
    """Serializer for video participants."""
    
    participant_name = serializers.SerializerMethodField()

    class Meta:
        model = VideoParticipant
        fields = [
            'id', 'room', 'user', 'guest_name', 'participant_name',
            'status', 'role', 'joined_at', 'left_at',
            'audio_enabled', 'video_enabled', 'screen_sharing',
            'connection_quality', 'device_info', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_participant_name(self, obj):
        return obj.user.email if obj.user else obj.guest_name


class VideoRoomSerializer(serializers.ModelSerializer):
    """Serializer for video rooms."""
    
    participants_count = serializers.SerializerMethodField()
    host_email = serializers.EmailField(source='host.email', read_only=True)

    class Meta:
        model = VideoRoom
        fields = [
            'id', 'workspace', 'room_id', 'name', 'description',
            'provider', 'provider_room_id', 'provider_data',
            'max_participants', 'require_password', 'password',
            'enable_recording', 'enable_screen_share', 'enable_chat',
            'status', 'scheduled_start', 'scheduled_end',
            'started_at', 'ended_at', 'peak_participants',
            'total_duration_minutes', 'host', 'host_email',
            'participants_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'room_id', 'started_at', 'ended_at',
            'peak_participants', 'total_duration_minutes',
            'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_participants_count(self, obj):
        return obj.participants.filter(status='joined').count()


class VideoRecordingSerializer(serializers.ModelSerializer):
    """Serializer for video recordings."""

    class Meta:
        model = VideoRecording
        fields = [
            'id', 'room', 'title', 'description', 'file_url',
            'file_size_mb', 'duration_seconds', 'format',
            'status', 'processing_error', 'recorded_at',
            'processed_at', 'metadata', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'file_size_mb', 'duration_seconds',
            'processed_at', 'created_at', 'updated_at'
        ]


class VideoInvitationSerializer(serializers.ModelSerializer):
    """Serializer for video invitations."""

    class Meta:
        model = VideoInvitation
        fields = [
            'id', 'room', 'inviter', 'invitee', 'invitee_email',
            'status', 'message', 'token', 'expires_at',
            'responded_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'token', 'status', 'responded_at', 'created_at'
        ]

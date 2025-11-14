"""
Meetings Serializers
"""

from rest_framework import serializers
from .models import Meeting, MeetingParticipant, MeetingNote, MeetingRecording
from users.serializers import UserSerializer


class MeetingParticipantSerializer(serializers.ModelSerializer):
    """Serializer for meeting participants."""

    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MeetingParticipant
        fields = [
            'id', 'user', 'user_id', 'role', 'status',
            'joined_at', 'left_at'
        ]
        read_only_fields = ['id', 'joined_at', 'left_at']


class MeetingNoteSerializer(serializers.ModelSerializer):
    """Serializer for meeting notes."""

    created_by = UserSerializer(read_only=True)

    class Meta:
        model = MeetingNote
        fields = [
            'id', 'meeting', 'title', 'content',
            'created_by', 'is_shared', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']


class MeetingRecordingSerializer(serializers.ModelSerializer):
    """Serializer for meeting recordings."""

    class Meta:
        model = MeetingRecording
        fields = [
            'id', 'meeting', 'recording_url', 'duration_seconds',
            'file_size', 'transcript_url', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MeetingSerializer(serializers.ModelSerializer):
    """Full serializer for meetings."""

    organizer = UserSerializer(read_only=True)
    participants_data = MeetingParticipantSerializer(
        source='participants_through',
        many=True,
        read_only=True
    )
    notes = MeetingNoteSerializer(many=True, read_only=True)
    recordings = MeetingRecordingSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'workspace', 'title', 'description',
            'meeting_type', 'status', 'start_time', 'end_time',
            'timezone', 'is_recurring', 'recurrence_rule',
            'recurrence_end_date', 'organizer', 'participants_data',
            'participant_count', 'meeting_url', 'meeting_id',
            'meeting_password', 'is_recorded', 'recording_url',
            'allow_guests', 'require_approval', 'notes', 'recordings',
            'duration_minutes', 'created_at', 'updated_at',
            'started_at', 'ended_at'
        ]
        read_only_fields = [
            'id', 'meeting_id', 'organizer', 'created_at',
            'updated_at', 'started_at', 'ended_at'
        ]

    def get_participant_count(self, obj):
        """Get total participant count."""
        return obj.participants.count()

    def get_duration_minutes(self, obj):
        """Get meeting duration in minutes."""
        return obj.duration_minutes()


class MeetingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for meeting lists."""

    organizer = UserSerializer(read_only=True)
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            'id', 'title', 'description', 'meeting_type',
            'status', 'start_time', 'end_time', 'organizer',
            'participant_count', 'is_recorded', 'meeting_url',
            'created_at'
        ]

    def get_participant_count(self, obj):
        """Get total participant count."""
        return obj.participants.count()


class MeetingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating meetings."""

    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Meeting
        fields = [
            'workspace', 'title', 'description', 'meeting_type',
            'start_time', 'end_time', 'timezone', 'is_recurring',
            'recurrence_rule', 'recurrence_end_date', 'participant_ids',
            'meeting_password', 'is_recorded', 'allow_guests',
            'require_approval'
        ]

    def create(self, validated_data):
        """Create meeting with participants."""
        participant_ids = validated_data.pop('participant_ids', [])
        meeting = Meeting.objects.create(**validated_data)

        # Add participants
        for user_id in participant_ids:
            MeetingParticipant.objects.create(
                meeting=meeting,
                user_id=user_id,
                role='participant'
            )

        return meeting

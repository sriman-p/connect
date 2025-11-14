"""
Meetings Views
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Meeting, MeetingParticipant, MeetingNote, MeetingRecording
from .serializers import (
    MeetingSerializer,
    MeetingListSerializer,
    MeetingCreateSerializer,
    MeetingParticipantSerializer,
    MeetingNoteSerializer,
    MeetingRecordingSerializer,
)


class MeetingViewSet(viewsets.ModelViewSet):
    """ViewSet for meetings."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return MeetingListSerializer
        elif self.action == 'create':
            return MeetingCreateSerializer
        return MeetingSerializer

    def get_queryset(self):
        """Return meetings for user's workspaces."""
        user = self.request.user
        return Meeting.objects.filter(
            workspace__members=user
        ).select_related('organizer', 'workspace').prefetch_related(
            'participants', 'notes', 'recordings'
        ).distinct().order_by('-start_time')

    def perform_create(self, serializer):
        """Set organizer to current user."""
        import uuid
        serializer.save(
            organizer=self.request.user,
            meeting_id=str(uuid.uuid4())
        )

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a meeting."""
        meeting = self.get_object()
        meeting.status = 'in_progress'
        meeting.started_at = timezone.now()
        meeting.save()

        return Response({
            'message': 'Meeting started.',
            'meeting': MeetingSerializer(meeting).data
        })

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a meeting."""
        meeting = self.get_object()
        meeting.status = 'completed'
        meeting.ended_at = timezone.now()
        meeting.save()

        return Response({
            'message': 'Meeting ended.',
            'meeting': MeetingSerializer(meeting).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a meeting."""
        meeting = self.get_object()
        meeting.status = 'cancelled'
        meeting.save()

        return Response({
            'message': 'Meeting cancelled.',
            'meeting': MeetingSerializer(meeting).data
        })

    @action(detail=True, methods=['get'])
    def participants(self, request, pk=None):
        """Get meeting participants."""
        meeting = self.get_object()
        participants = MeetingParticipant.objects.filter(
            meeting=meeting
        ).select_related('user')

        serializer = MeetingParticipantSerializer(participants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a meeting."""
        meeting = self.get_object()

        participant, created = MeetingParticipant.objects.get_or_create(
            meeting=meeting,
            user=request.user,
            defaults={'role': 'participant', 'status': 'joined'}
        )

        if not created:
            participant.status = 'joined'
            participant.joined_at = timezone.now()
            participant.save()

        return Response({
            'message': 'Joined meeting.',
            'participant': MeetingParticipantSerializer(participant).data
        })

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a meeting."""
        meeting = self.get_object()

        try:
            participant = MeetingParticipant.objects.get(
                meeting=meeting,
                user=request.user
            )
            participant.status = 'left'
            participant.left_at = timezone.now()
            participant.save()

            return Response({
                'message': 'Left meeting.',
                'participant': MeetingParticipantSerializer(participant).data
            })
        except MeetingParticipant.DoesNotExist:
            return Response({
                'error': 'You are not a participant of this meeting.'
            }, status=status.HTTP_400_BAD_REQUEST)


class MeetingNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for meeting notes."""

    serializer_class = MeetingNoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return notes for user's meetings."""
        user = self.request.user
        return MeetingNote.objects.filter(
            meeting__workspace__members=user
        ).select_related('meeting', 'created_by').distinct()

    def perform_create(self, serializer):
        """Set creator to current user."""
        serializer.save(created_by=self.request.user)


class MeetingRecordingViewSet(viewsets.ModelViewSet):
    """ViewSet for meeting recordings."""

    serializer_class = MeetingRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return recordings for user's meetings."""
        user = self.request.user
        return MeetingRecording.objects.filter(
            meeting__workspace__members=user
        ).select_related('meeting').distinct()

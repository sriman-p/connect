"""
Video Conferencing Views
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import VideoRoom, VideoParticipant, VideoRecording, VideoInvitation
from .serializers import (
    VideoRoomSerializer,
    VideoParticipantSerializer,
    VideoRecordingSerializer,
    VideoInvitationSerializer,
)


class VideoRoomViewSet(viewsets.ModelViewSet):
    """ViewSet for video rooms."""

    serializer_class = VideoRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return rooms for user's workspaces."""
        user = self.request.user
        return VideoRoom.objects.filter(
            workspace__members=user
        ).select_related('workspace', 'host').distinct()

    def perform_create(self, serializer):
        """Create video room."""
        serializer.save(host=self.request.user)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a video room."""
        room = self.get_object()
        
        if room.status != 'scheduled':
            return Response({
                'error': 'Room is not in scheduled status'
            }, status=status.HTTP_400_BAD_REQUEST)

        room.status = 'active'
        room.started_at = timezone.now()
        room.save()

        return Response({
            'status': 'success',
            'message': 'Room started',
            'room_id': room.room_id
        })

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a video room."""
        room = self.get_object()
        
        if room.status != 'active':
            return Response({
                'error': 'Room is not active'
            }, status=status.HTTP_400_BAD_REQUEST)

        room.status = 'ended'
        room.ended_at = timezone.now()
        
        # Calculate duration
        if room.started_at:
            duration = (room.ended_at - room.started_at).total_seconds() / 60
            room.total_duration_minutes = int(duration)
        
        room.save()

        return Response({
            'status': 'success',
            'message': 'Room ended',
            'duration_minutes': room.total_duration_minutes
        })

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a video room."""
        room = self.get_object()
        user = request.user

        # Check if room is active
        if room.status != 'active':
            return Response({
                'error': 'Room is not active'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get or create participant
        participant, created = VideoParticipant.objects.get_or_create(
            room=room,
            user=user,
            defaults={
                'status': 'joined',
                'joined_at': timezone.now()
            }
        )

        if not created:
            participant.status = 'joined'
            participant.joined_at = timezone.now()
            participant.save()

        # Update peak participants
        current_participants = room.participants.filter(status='joined').count()
        if current_participants > room.peak_participants:
            room.peak_participants = current_participants
            room.save()

        return Response({
            'status': 'success',
            'message': 'Joined room',
            'participant_id': participant.id
        })

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a video room."""
        room = self.get_object()
        user = request.user

        try:
            participant = VideoParticipant.objects.get(room=room, user=user)
            participant.status = 'left'
            participant.left_at = timezone.now()
            participant.save()

            return Response({
                'status': 'success',
                'message': 'Left room'
            })
        except VideoParticipant.DoesNotExist:
            return Response({
                'error': 'Participant not found'
            }, status=status.HTTP_404_NOT_FOUND)


class VideoParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for video participants (read-only)."""

    serializer_class = VideoParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return participants for user's rooms."""
        user = self.request.user
        return VideoParticipant.objects.filter(
            room__workspace__members=user
        ).select_related('room', 'user').distinct()


class VideoRecordingViewSet(viewsets.ModelViewSet):
    """ViewSet for video recordings."""

    serializer_class = VideoRecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return recordings for user's rooms."""
        user = self.request.user
        return VideoRecording.objects.filter(
            room__workspace__members=user
        ).select_related('room').distinct()


class VideoInvitationViewSet(viewsets.ModelViewSet):
    """ViewSet for video invitations."""

    serializer_class = VideoInvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return invitations for user."""
        user = self.request.user
        return VideoInvitation.objects.filter(
            invitee=user
        ).select_related('room', 'inviter').distinct()

    def perform_create(self, serializer):
        """Create invitation."""
        expires_at = timezone.now() + timedelta(days=7)
        serializer.save(inviter=self.request.user, expires_at=expires_at)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept an invitation."""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response({
                'error': 'Invitation is not pending'
            }, status=status.HTTP_400_BAD_REQUEST)

        invitation.status = 'accepted'
        invitation.responded_at = timezone.now()
        invitation.save()

        return Response({
            'status': 'success',
            'message': 'Invitation accepted',
            'room_id': invitation.room.room_id
        })

    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline an invitation."""
        invitation = self.get_object()
        
        if invitation.status != 'pending':
            return Response({
                'error': 'Invitation is not pending'
            }, status=status.HTTP_400_BAD_REQUEST)

        invitation.status = 'declined'
        invitation.responded_at = timezone.now()
        invitation.save()

        return Response({
            'status': 'success',
            'message': 'Invitation declined'
        })

from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Channel, ChannelMember, Message, MessageReaction, MessageAttachment
from .serializers import (
    ChannelSerializer,
    ChannelMemberSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageReactionSerializer,
    ChannelCreateSerializer,
)

User = get_user_model()


class ChannelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Channel CRUD operations.
    Endpoints:
    - GET /api/channels/ - List channels
    - POST /api/channels/ - Create channel
    - GET /api/channels/{id}/ - Get channel details
    - PATCH /api/channels/{id}/ - Update channel
    - DELETE /api/channels/{id}/ - Archive channel
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == 'create':
            return ChannelCreateSerializer
        return ChannelSerializer

    def get_queryset(self):
        """Return channels user has access to."""
        user = self.request.user
        workspace_id = self.request.query_params.get('workspace')

        # User can see channels they're a member of
        queryset = Channel.objects.filter(
            channel_members__user=user,
            is_archived=False
        ).distinct().select_related('workspace', 'created_by')

        # Filter by workspace
        if workspace_id:
            queryset = queryset.filter(workspace_id=workspace_id)

        return queryset

    def perform_create(self, serializer):
        """Create channel and add creator as member."""
        workspace_id = self.request.data.get('workspace')

        # Validate workspace access
        from workspaces.models import Workspace, WorkspaceMember
        try:
            workspace = Workspace.objects.get(id=workspace_id)
            WorkspaceMember.objects.get(
                workspace=workspace,
                user=self.request.user,
                is_active=True
            )
        except (Workspace.DoesNotExist, WorkspaceMember.DoesNotExist):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have access to this workspace.')

        channel = serializer.save(created_by=self.request.user)

        # Add creator as member
        ChannelMember.objects.create(
            channel=channel,
            user=self.request.user
        )

    def destroy(self, request, *args, **kwargs):
        """Archive channel instead of deleting."""
        instance = self.get_object()
        instance.is_archived = True
        instance.save()

        return Response({
            'message': 'Channel archived successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """
        Get all members of a channel.
        GET /api/channels/{id}/members/
        """
        channel = self.get_object()
        members = channel.channel_members.all().select_related('user')
        serializer = ChannelMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Join a channel.
        POST /api/channels/{id}/join/
        """
        channel = self.get_object()
        user = request.user

        # Check if already a member
        if ChannelMember.objects.filter(channel=channel, user=user).exists():
            return Response({
                'error': 'You are already a member of this channel.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create membership
        member = ChannelMember.objects.create(
            channel=channel,
            user=user
        )

        return Response({
            'message': 'Joined channel successfully.',
            'member': ChannelMemberSerializer(member).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """
        Leave a channel.
        POST /api/channels/{id}/leave/
        """
        channel = self.get_object()
        user = request.user

        try:
            member = ChannelMember.objects.get(channel=channel, user=user)
            member.delete()

            return Response({
                'message': 'Left channel successfully.'
            }, status=status.HTTP_200_OK)
        except ChannelMember.DoesNotExist:
            return Response({
                'error': 'You are not a member of this channel.'
            }, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark all messages in channel as read.
        POST /api/channels/{id}/mark_read/
        """
        channel = self.get_object()
        user = request.user

        try:
            member = ChannelMember.objects.get(channel=channel, user=user)
            member.last_read_at = timezone.now()
            member.save(update_fields=['last_read_at'])

            return Response({
                'message': 'Channel marked as read.'
            }, status=status.HTTP_200_OK)
        except ChannelMember.DoesNotExist:
            return Response({
                'error': 'You are not a member of this channel.'
            }, status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message CRUD operations.
    Endpoints:
    - GET /api/messages/ - List messages
    - POST /api/messages/ - Send message
    - GET /api/messages/{id}/ - Get message details
    - PATCH /api/messages/{id}/ - Update message
    - DELETE /api/messages/{id}/ - Delete message
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializer for create."""
        if self.action == 'create':
            return MessageCreateSerializer
        return MessageSerializer

    def get_queryset(self):
        """Return messages user has access to."""
        user = self.request.user
        channel_id = self.request.query_params.get('channel')

        # User can see messages in channels they're a member of
        queryset = Message.objects.filter(
            channel__channel_members__user=user,
            is_deleted=False
        ).distinct().select_related(
            'channel',
            'author',
            'parent_message'
        ).prefetch_related('reactions', 'attachments')

        # Filter by channel
        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)

        # Order by created_at
        queryset = queryset.order_by('created_at')

        return queryset

    def perform_create(self, serializer):
        """Send message."""
        channel_id = self.request.data.get('channel')

        # Validate channel access
        try:
            channel = Channel.objects.get(id=channel_id)
            ChannelMember.objects.get(
                channel=channel,
                user=self.request.user
            )
        except (Channel.DoesNotExist, ChannelMember.DoesNotExist):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You do not have access to this channel.')

        # Save message
        message = serializer.save(author=self.request.user)

        # Update parent message thread count if replying
        if message.parent_message:
            parent = message.parent_message
            parent.thread_reply_count += 1
            parent.save(update_fields=['thread_reply_count'])

    def perform_update(self, serializer):
        """Update message and mark as edited."""
        serializer.save(is_edited=True)

    def destroy(self, request, *args, **kwargs):
        """Soft delete message."""
        instance = self.get_object()

        # Only author can delete
        if instance.author != request.user:
            return Response({
                'error': 'You can only delete your own messages.'
            }, status=status.HTTP_403_FORBIDDEN)

        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])

        return Response({
            'message': 'Message deleted successfully.'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def react(self, request, pk=None):
        """
        Add reaction to message.
        POST /api/messages/{id}/react/
        Body: {"emoji": "👍"}
        """
        message = self.get_object()
        emoji = request.data.get('emoji')

        if not emoji:
            return Response({
                'error': 'Emoji is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if user already reacted with this emoji
        existing = MessageReaction.objects.filter(
            message=message,
            user=request.user,
            emoji=emoji
        ).first()

        if existing:
            # Remove reaction (toggle)
            existing.delete()
            return Response({
                'message': 'Reaction removed.',
                'action': 'removed'
            }, status=status.HTTP_200_OK)

        # Add reaction
        reaction = MessageReaction.objects.create(
            message=message,
            user=request.user,
            emoji=emoji
        )

        return Response({
            'message': 'Reaction added.',
            'action': 'added',
            'reaction': MessageReactionSerializer(reaction).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """
        Get thread replies for a message.
        GET /api/messages/{id}/thread/
        """
        message = self.get_object()
        replies = message.thread_replies.filter(
            is_deleted=False
        ).select_related('author').order_by('created_at')

        serializer = MessageSerializer(replies, many=True)
        return Response(serializer.data)

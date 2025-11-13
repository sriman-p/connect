from rest_framework import serializers
from .models import Channel, ChannelMember, Message, MessageReaction, MessageAttachment
from users.serializers import UserSerializer


class ChannelSerializer(serializers.ModelSerializer):
    """Serializer for Channel model."""

    workspace_data = serializers.SerializerMethodField()
    created_by_data = UserSerializer(source='created_by', read_only=True)
    member_count = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Channel
        fields = [
            'id',
            'workspace',
            'workspace_data',
            'name',
            'slug',
            'description',
            'channel_type',
            'created_by',
            'created_by_data',
            'is_archived',
            'member_count',
            'unread_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

    def get_workspace_data(self, obj):
        """Get workspace data."""
        from workspaces.serializers import WorkspaceSerializer
        return WorkspaceSerializer(obj.workspace).data if obj.workspace else None

    def get_member_count(self, obj):
        """Get total member count."""
        return obj.channel_members.count()

    def get_unread_count(self, obj):
        """Get unread message count for current user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 0

        try:
            member = obj.channel_members.get(user=request.user)
            if member.last_read_at:
                return obj.messages.filter(
                    created_at__gt=member.last_read_at,
                    is_deleted=False
                ).count()
        except ChannelMember.DoesNotExist:
            pass

        return 0


class ChannelMemberSerializer(serializers.ModelSerializer):
    """Serializer for ChannelMember model."""

    user_data = UserSerializer(source='user', read_only=True)
    channel_data = ChannelSerializer(source='channel', read_only=True)

    class Meta:
        model = ChannelMember
        fields = [
            'id',
            'channel',
            'channel_data',
            'user',
            'user_data',
            'mute_notifications',
            'last_read_at',
            'joined_at',
        ]
        read_only_fields = ['id', 'joined_at']


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for MessageReaction model."""

    user_data = UserSerializer(source='user', read_only=True)

    class Meta:
        model = MessageReaction
        fields = [
            'id',
            'message',
            'user',
            'user_data',
            'emoji',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


class MessageAttachmentSerializer(serializers.ModelSerializer):
    """Serializer for MessageAttachment model."""

    class Meta:
        model = MessageAttachment
        fields = [
            'id',
            'message',
            'file_name',
            'file_url',
            'file_size',
            'file_type',
            'thumbnail_url',
            'uploaded_at',
        ]
        read_only_fields = ['id', 'uploaded_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model."""

    author_data = UserSerializer(source='author', read_only=True)
    channel_data = ChannelSerializer(source='channel', read_only=True)
    parent_message_data = serializers.SerializerMethodField()
    reactions = MessageReactionSerializer(many=True, read_only=True)
    attachments = MessageAttachmentSerializer(many=True, read_only=True)
    reaction_summary = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'id',
            'channel',
            'channel_data',
            'author',
            'author_data',
            'content',
            'message_type',
            'parent_message',
            'parent_message_data',
            'thread_reply_count',
            'mentions',
            'reactions',
            'attachments',
            'reaction_summary',
            'is_edited',
            'is_deleted',
            'created_at',
            'updated_at',
            'deleted_at',
        ]
        read_only_fields = [
            'id',
            'author',
            'is_edited',
            'is_deleted',
            'created_at',
            'updated_at',
            'deleted_at',
        ]

    def get_parent_message_data(self, obj):
        """Get parent message data (simplified to avoid recursion)."""
        if obj.parent_message and not obj.parent_message.is_deleted:
            return {
                'id': obj.parent_message.id,
                'author': UserSerializer(obj.parent_message.author).data,
                'content': obj.parent_message.content[:100],  # Truncate
                'created_at': obj.parent_message.created_at,
            }
        return None

    def get_reaction_summary(self, obj):
        """Get reaction summary (emoji counts)."""
        reactions = obj.reactions.all()
        summary = {}

        for reaction in reactions:
            emoji = reaction.emoji
            if emoji not in summary:
                summary[emoji] = {
                    'emoji': emoji,
                    'count': 0,
                    'users': []
                }
            summary[emoji]['count'] += 1
            summary[emoji]['users'].append({
                'id': reaction.user.id,
                'email': reaction.user.email,
                'full_name': reaction.user.full_name,
            })

        return list(summary.values())


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages."""

    class Meta:
        model = Message
        fields = [
            'channel',
            'content',
            'message_type',
            'parent_message',
            'mentions',
        ]


class ChannelCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating channels."""

    class Meta:
        model = Channel
        fields = [
            'workspace',
            'name',
            'slug',
            'description',
            'channel_type',
        ]

    def validate_slug(self, value):
        """Validate slug is unique within workspace."""
        workspace = self.initial_data.get('workspace')
        if workspace and Channel.objects.filter(
            workspace_id=workspace,
            slug=value
        ).exists():
            raise serializers.ValidationError(
                'A channel with this slug already exists in this workspace.'
            )
        return value

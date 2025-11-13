from django.db import models
from django.conf import settings


class Channel(models.Model):
    """
    Channel model for team communication.
    Slack-style channels with public/private support.
    """

    # Channel types
    PUBLIC = 'public'
    PRIVATE = 'private'
    DIRECT = 'direct'

    CHANNEL_TYPE_CHOICES = [
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
        (DIRECT, 'Direct Message'),
    ]

    # Core fields
    workspace = models.ForeignKey(
        'workspaces.Workspace',
        on_delete=models.CASCADE,
        related_name='channels',
        help_text='Associated workspace'
    )
    name = models.CharField(
        max_length=100,
        help_text='Channel name'
    )
    slug = models.SlugField(
        max_length=100,
        help_text='URL-friendly channel identifier'
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        default='',
        help_text='Channel description'
    )

    # Channel type and visibility
    channel_type = models.CharField(
        max_length=20,
        choices=CHANNEL_TYPE_CHOICES,
        default=PUBLIC,
        db_index=True,
        help_text='Channel type'
    )

    # Members (for private channels and DMs)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChannelMember',
        related_name='channels',
        help_text='Channel members'
    )

    # Creator and settings
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_channels',
        help_text='Channel creator'
    )
    is_archived = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Channel is archived'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Channel creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )

    class Meta:
        db_table = 'channels'
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'
        ordering = ['name']
        unique_together = [['workspace', 'slug']]
        indexes = [
            models.Index(fields=['workspace', 'channel_type']),
            models.Index(fields=['workspace', 'is_archived']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"#{self.name}"


class ChannelMember(models.Model):
    """
    Channel membership model.
    Tracks who has access to channels and their notification preferences.
    """

    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='channel_members',
        help_text='Associated channel'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='channel_memberships',
        help_text='Member user'
    )

    # Notification settings
    mute_notifications = models.BooleanField(
        default=False,
        help_text='Mute channel notifications'
    )
    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time user read messages'
    )

    # Timestamps
    joined_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Member joined timestamp'
    )

    class Meta:
        db_table = 'channel_members'
        verbose_name = 'Channel Member'
        verbose_name_plural = 'Channel Members'
        unique_together = [['channel', 'user']]
        indexes = [
            models.Index(fields=['channel', 'user']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.channel.name}"


class Message(models.Model):
    """
    Message model for channel communications.
    Supports text, mentions, reactions, and threading.
    """

    # Message types
    TEXT = 'text'
    SYSTEM = 'system'
    ATTACHMENT = 'attachment'

    MESSAGE_TYPE_CHOICES = [
        (TEXT, 'Text'),
        (SYSTEM, 'System'),
        (ATTACHMENT, 'Attachment'),
    ]

    # Core fields
    channel = models.ForeignKey(
        Channel,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='Associated channel'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text='Message author'
    )
    content = models.TextField(
        help_text='Message content (supports markdown)'
    )

    # Message type
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default=TEXT,
        help_text='Message type'
    )

    # Threading support
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='thread_replies',
        help_text='Parent message for threaded replies'
    )
    thread_reply_count = models.IntegerField(
        default=0,
        help_text='Number of thread replies'
    )

    # Mentions (stored as JSON array of user IDs)
    # Format: [user_id1, user_id2, ...]
    mentions = models.JSONField(
        default=list,
        blank=True,
        help_text='User IDs mentioned in message'
    )

    # Status
    is_edited = models.BooleanField(
        default=False,
        help_text='Message has been edited'
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Message is deleted'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text='Message creation timestamp'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last update timestamp'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Message deletion timestamp'
    )

    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['channel', 'created_at']),
            models.Index(fields=['channel', 'is_deleted', 'created_at']),
            models.Index(fields=['author']),
            models.Index(fields=['parent_message', 'created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Message by {self.author.email} in {self.channel.name}"


class MessageReaction(models.Model):
    """
    Message reaction model for emoji reactions.
    Slack-style message reactions.
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions',
        help_text='Associated message'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_reactions',
        help_text='User who reacted'
    )
    emoji = models.CharField(
        max_length=50,
        help_text='Emoji unicode or name'
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Reaction creation timestamp'
    )

    class Meta:
        db_table = 'message_reactions'
        verbose_name = 'Message Reaction'
        verbose_name_plural = 'Message Reactions'
        unique_together = [['message', 'user', 'emoji']]
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.emoji} by {self.user.email}"


class MessageAttachment(models.Model):
    """
    Message attachment model for files sent in messages.
    """

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text='Associated message'
    )
    file_name = models.CharField(
        max_length=255,
        help_text='Original file name'
    )
    file_url = models.URLField(
        max_length=1000,
        help_text='URL to file (S3/storage)'
    )
    file_size = models.IntegerField(
        help_text='File size in bytes'
    )
    file_type = models.CharField(
        max_length=100,
        help_text='File MIME type'
    )
    thumbnail_url = models.URLField(
        max_length=1000,
        blank=True,
        null=True,
        help_text='Thumbnail URL for images/videos'
    )

    # Timestamps
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Upload timestamp'
    )

    class Meta:
        db_table = 'message_attachments'
        verbose_name = 'Message Attachment'
        verbose_name_plural = 'Message Attachments'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['message']),
        ]

    def __str__(self):
        return f"{self.file_name} in {self.message.channel.name}"

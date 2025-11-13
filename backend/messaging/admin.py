from django.contrib import admin
from .models import Channel, ChannelMember, Message, MessageReaction, MessageAttachment


class ChannelMemberInline(admin.TabularInline):
    """Inline admin for channel members."""
    model = ChannelMember
    extra = 0
    fields = ['user', 'mute_notifications', 'last_read_at', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Admin interface for Channel model."""

    list_display = [
        'name',
        'workspace',
        'channel_type',
        'created_by',
        'is_archived',
        'created_at',
    ]
    list_filter = ['channel_type', 'is_archived', 'workspace', 'created_at']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ChannelMemberInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('workspace', 'name', 'slug', 'description')
        }),
        ('Settings', {
            'fields': ('channel_type', 'created_by', 'is_archived')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(ChannelMember)
class ChannelMemberAdmin(admin.ModelAdmin):
    """Admin interface for ChannelMember model."""

    list_display = ['user', 'channel', 'mute_notifications', 'joined_at']
    list_filter = ['mute_notifications', 'joined_at']
    search_fields = ['user__email', 'channel__name']
    readonly_fields = ['joined_at']

    fieldsets = (
        ('Membership', {
            'fields': ('channel', 'user')
        }),
        ('Settings', {
            'fields': ('mute_notifications', 'last_read_at')
        }),
        ('Timestamps', {
            'fields': ('joined_at',)
        }),
    )


class MessageReactionInline(admin.TabularInline):
    """Inline admin for message reactions."""
    model = MessageReaction
    extra = 0
    fields = ['user', 'emoji', 'created_at']
    readonly_fields = ['created_at']


class MessageAttachmentInline(admin.TabularInline):
    """Inline admin for message attachments."""
    model = MessageAttachment
    extra = 0
    fields = ['file_name', 'file_url', 'file_size', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model."""

    list_display = [
        'id',
        'channel',
        'author',
        'message_type',
        'is_edited',
        'is_deleted',
        'created_at',
    ]
    list_filter = [
        'message_type',
        'is_edited',
        'is_deleted',
        'channel',
        'created_at',
    ]
    search_fields = ['content', 'author__email', 'channel__name']
    readonly_fields = [
        'author',
        'is_edited',
        'is_deleted',
        'created_at',
        'updated_at',
        'deleted_at',
    ]
    inlines = [MessageReactionInline, MessageAttachmentInline]

    fieldsets = (
        ('Message Content', {
            'fields': ('channel', 'author', 'content', 'message_type')
        }),
        ('Threading', {
            'fields': ('parent_message', 'thread_reply_count')
        }),
        ('Metadata', {
            'fields': ('mentions', 'is_edited', 'is_deleted')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'deleted_at')
        }),
    )


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    """Admin interface for MessageReaction model."""

    list_display = ['message', 'user', 'emoji', 'created_at']
    list_filter = ['emoji', 'created_at']
    search_fields = ['message__content', 'user__email']
    readonly_fields = ['created_at']


@admin.register(MessageAttachment)
class MessageAttachmentAdmin(admin.ModelAdmin):
    """Admin interface for MessageAttachment model."""

    list_display = [
        'file_name',
        'message',
        'file_size',
        'file_type',
        'uploaded_at',
    ]
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['file_name', 'message__content']
    readonly_fields = ['uploaded_at']

    fieldsets = (
        ('File Information', {
            'fields': ('message', 'file_name', 'file_url', 'file_size', 'file_type')
        }),
        ('Preview', {
            'fields': ('thumbnail_url',)
        }),
        ('Metadata', {
            'fields': ('uploaded_at',)
        }),
    )

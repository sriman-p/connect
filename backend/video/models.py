"""
Video Conferencing Models
Built-in video call rooms and management
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from users.models import User
from workspaces.models import Workspace
import uuid


class VideoRoom(models.Model):
    """Video conference room."""

    ROOM_STATUS = [
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('ended', 'Ended'),
        ('cancelled', 'Cancelled'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='video_rooms')
    room_id = models.CharField(max_length=100, unique=True, db_index=True)

    # Room details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # Generic relation to any object (meeting, project, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Provider settings
    provider = models.CharField(
        max_length=20,
        choices=[
            ('jitsi', 'Jitsi'),
            ('zoom', 'Zoom'),
            ('webrtc', 'WebRTC'),
        ],
        default='jitsi'
    )
    provider_room_id = models.CharField(max_length=200, blank=True)
    provider_data = models.JSONField(default=dict, blank=True)

    # Room settings
    max_participants = models.IntegerField(default=50)
    require_password = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True)
    enable_recording = models.BooleanField(default=False)
    enable_screen_share = models.BooleanField(default=True)
    enable_chat = models.BooleanField(default=True)

    # Status
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='scheduled')

    # Schedule
    scheduled_start = models.DateTimeField(null=True, blank=True)
    scheduled_end = models.DateTimeField(null=True, blank=True)

    # Actual times
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    # Statistics
    peak_participants = models.IntegerField(default=0)
    total_duration_minutes = models.IntegerField(default=0)

    # Host
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_rooms')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['workspace', 'status', '-created_at']),
            models.Index(fields=['room_id']),
        ]

    def __str__(self):
        return f"{self.name} ({self.room_id})"

    def save(self, *args, **kwargs):
        if not self.room_id:
            self.room_id = str(uuid.uuid4())
        super().save(*args, **kwargs)


class VideoParticipant(models.Model):
    """Participant in a video room."""

    PARTICIPANT_STATUS = [
        ('invited', 'Invited'),
        ('joined', 'Joined'),
        ('left', 'Left'),
        ('kicked', 'Kicked'),
    ]

    PARTICIPANT_ROLE = [
        ('host', 'Host'),
        ('moderator', 'Moderator'),
        ('participant', 'Participant'),
        ('guest', 'Guest'),
    ]

    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    guest_name = models.CharField(max_length=100, blank=True)  # For guests without accounts

    # Status and role
    status = models.CharField(max_length=20, choices=PARTICIPANT_STATUS, default='invited')
    role = models.CharField(max_length=20, choices=PARTICIPANT_ROLE, default='participant')

    # Join/leave times
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)

    # Settings
    audio_enabled = models.BooleanField(default=True)
    video_enabled = models.BooleanField(default=True)
    screen_sharing = models.BooleanField(default=False)

    # Connection info
    connection_quality = models.CharField(max_length=20, blank=True)  # excellent, good, poor
    device_info = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['room', 'user']
        indexes = [
            models.Index(fields=['room', 'status']),
        ]

    def __str__(self):
        name = self.user.email if self.user else self.guest_name
        return f"{name} in {self.room.name}"


class VideoRecording(models.Model):
    """Recording of a video room session."""

    RECORDING_STATUS = [
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
        ('deleted', 'Deleted'),
    ]

    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='recordings')

    # Recording details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    # File storage
    file_url = models.URLField(max_length=500, blank=True)
    file_size_mb = models.FloatField(default=0)
    duration_seconds = models.IntegerField(default=0)
    format = models.CharField(max_length=20, default='mp4')

    # Processing
    status = models.CharField(max_length=20, choices=RECORDING_STATUS, default='processing')
    processing_error = models.TextField(blank=True)

    # Timestamps
    recorded_at = models.DateTimeField()
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Metadata
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Recording: {self.title}"


class VideoInvitation(models.Model):
    """Invitation to join a video room."""

    INVITATION_STATUS = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    room = models.ForeignKey(VideoRoom, on_delete=models.CASCADE, related_name='invitations')
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_video_invitations')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_video_invitations', null=True, blank=True)
    invitee_email = models.EmailField(blank=True)  # For external guests

    # Status
    status = models.CharField(max_length=20, choices=INVITATION_STATUS, default='pending')

    # Invitation details
    message = models.TextField(blank=True)
    token = models.CharField(max_length=100, unique=True)
    expires_at = models.DateTimeField()

    # Response
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        email = self.invitee.email if self.invitee else self.invitee_email
        return f"Invitation to {email} for {self.room.name}"

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)

"""
Meetings Models
Video conferencing, calendar, and scheduling
"""

from django.db import models
from django.utils import timezone
from users.models import User
from workspaces.models import Workspace


class Meeting(models.Model):
    """Meeting or video call."""

    MEETING_TYPE_CHOICES = [
        ('instant', 'Instant Meeting'),
        ('scheduled', 'Scheduled Meeting'),
        ('recurring', 'Recurring Meeting'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='meetings'
    )

    # Meeting details
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    meeting_type = models.CharField(max_length=20, choices=MEETING_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Scheduling
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    timezone = models.CharField(max_length=50, default='UTC')

    # Recurring meetings
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=200, blank=True)  # RRULE format
    recurrence_end_date = models.DateTimeField(null=True, blank=True)

    # Participants
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_meetings'
    )
    participants = models.ManyToManyField(
        User,
        through='MeetingParticipant',
        related_name='meetings'
    )

    # Meeting room details
    meeting_url = models.URLField(blank=True)  # Video call URL
    meeting_id = models.CharField(max_length=100, unique=True)
    meeting_password = models.CharField(max_length=50, blank=True)

    # Settings
    is_recorded = models.BooleanField(default=False)
    recording_url = models.URLField(blank=True)
    allow_guests = models.BooleanField(default=True)
    require_approval = models.BooleanField(default=False)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['workspace', 'start_time']),
            models.Index(fields=['organizer', 'start_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.title} - {self.start_time}"

    def duration_minutes(self):
        """Calculate meeting duration in minutes."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() / 60)
        return 0

    def is_happening_now(self):
        """Check if meeting is currently in progress."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'in_progress'


class MeetingParticipant(models.Model):
    """Meeting participant with response status."""

    RESPONSE_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('tentative', 'Tentative'),
    ]

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Response
    response = models.CharField(
        max_length=20,
        choices=RESPONSE_CHOICES,
        default='pending'
    )
    response_message = models.TextField(blank=True)

    # Attendance
    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=0)

    # Permissions
    is_presenter = models.BooleanField(default=False)
    is_moderator = models.BooleanField(default=False)
    can_share_screen = models.BooleanField(default=True)
    can_unmute_self = models.BooleanField(default=True)

    # Metadata
    invited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['meeting', 'user']
        ordering = ['-invited_at']

    def __str__(self):
        return f"{self.user.email} - {self.meeting.title}"


class CalendarEvent(models.Model):
    """Calendar event (non-meeting events)."""

    EVENT_TYPE_CHOICES = [
        ('task', 'Task'),
        ('reminder', 'Reminder'),
        ('deadline', 'Deadline'),
        ('out_of_office', 'Out of Office'),
        ('holiday', 'Holiday'),
        ('other', 'Other'),
    ]

    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name='calendar_events'
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)

    # Timing
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_all_day = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, default='UTC')

    # Recurring events
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.CharField(max_length=200, blank=True)

    # Owner and attendees
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_events'
    )
    attendees = models.ManyToManyField(User, related_name='calendar_events', blank=True)

    # Reminders
    reminder_minutes_before = models.IntegerField(default=15)

    # Metadata
    color = models.CharField(max_length=7, default='#3b82f6')  # Hex color
    location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['workspace', 'start_time']),
            models.Index(fields=['created_by', 'start_time']),
        ]

    def __str__(self):
        return f"{self.title} - {self.start_time}"


class MeetingNote(models.Model):
    """Meeting notes and minutes."""

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='notes'
    )

    author = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    # Action items from meeting
    action_items = models.JSONField(default=list, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notes for {self.meeting.title}"


class MeetingRecording(models.Model):
    """Meeting recording metadata."""

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='recordings'
    )

    title = models.CharField(max_length=200)
    file_url = models.URLField()
    file_size = models.BigIntegerField()  # Bytes
    duration_seconds = models.IntegerField()

    # Transcript
    transcript_url = models.URLField(blank=True)
    has_transcript = models.BooleanField(default=False)

    # Metadata
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Recording: {self.meeting.title}"

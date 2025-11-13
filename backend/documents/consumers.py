"""
WebSocket consumers for real-time document collaboration.
Handles cursor positions, selections, and operational transformations.
"""

import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class DocumentCollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time document collaboration.
    Supports cursor tracking, selections, and operational transformation.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.document_id = self.scope['url_route']['kwargs']['document_id']
        self.room_group_name = f'document_{self.document_id}'
        self.user = self.scope['user']
        self.session_id = str(uuid.uuid4())

        # Assign a color for this user's cursor
        self.user_color = self._generate_user_color()

        # Join document room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Create session in database
        await self.create_session()

        # Notify other users that someone joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user_id': self.user.id,
                'user_email': self.user.email,
                'user_name': self.user.full_name,
                'session_id': self.session_id,
                'user_color': self.user_color,
            }
        )

        # Send active users to the new user
        active_users = await self.get_active_sessions()
        await self.send(text_data=json.dumps({
            'type': 'active_users',
            'users': active_users
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Mark session as inactive
        await self.deactivate_session()

        # Notify others that user left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user_id': self.user.id,
                'session_id': self.session_id,
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'cursor_move':
            # Broadcast cursor position to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cursor_update',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'cursor_position': data.get('cursor_position'),
                }
            )
            # Update session in database
            await self.update_cursor_position(data.get('cursor_position'))

        elif message_type == 'selection_change':
            # Broadcast selection to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'selection_update',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'selection_range': data.get('selection_range'),
                }
            )
            # Update session in database
            await self.update_selection(data.get('selection_range'))

        elif message_type == 'content_change':
            # Handle operational transformation
            operation = data.get('operation')
            base_version = data.get('base_version')
            sequence_number = data.get('sequence_number')

            # Save operation to database
            await self.save_operation(operation, base_version, sequence_number)

            # Broadcast to all other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'content_update',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'operation': operation,
                    'base_version': base_version,
                    'sequence_number': sequence_number,
                }
            )

        elif message_type == 'heartbeat':
            # Update last activity timestamp
            await self.update_activity()
            await self.send(text_data=json.dumps({
                'type': 'heartbeat_ack'
            }))

    # Group message handlers
    async def user_joined(self, event):
        """Send user joined event to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'user_joined',
                'user_id': event['user_id'],
                'user_email': event['user_email'],
                'user_name': event['user_name'],
                'session_id': event['session_id'],
                'user_color': event['user_color'],
            }))

    async def user_left(self, event):
        """Send user left event to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'user_left',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
            }))

    async def cursor_update(self, event):
        """Send cursor update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'cursor_update',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'cursor_position': event['cursor_position'],
            }))

    async def selection_update(self, event):
        """Send selection update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'selection_update',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'selection_range': event['selection_range'],
            }))

    async def content_update(self, event):
        """Send content update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'content_update',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'operation': event['operation'],
                'base_version': event['base_version'],
                'sequence_number': event['sequence_number'],
            }))

    # Database operations
    @database_sync_to_async
    def create_session(self):
        """Create a new document session."""
        from documents.models import DocumentSession, Document

        document = Document.objects.get(id=self.document_id)
        session = DocumentSession.objects.create(
            document=document,
            user=self.user,
            session_id=self.session_id,
            user_color=self.user_color,
            is_active=True
        )
        return session.id

    @database_sync_to_async
    def deactivate_session(self):
        """Mark session as inactive."""
        from documents.models import DocumentSession

        DocumentSession.objects.filter(
            session_id=self.session_id
        ).update(is_active=False)

    @database_sync_to_async
    def update_cursor_position(self, cursor_position):
        """Update cursor position in database."""
        from documents.models import DocumentSession

        DocumentSession.objects.filter(
            session_id=self.session_id
        ).update(
            cursor_position=cursor_position,
            last_activity_at=timezone.now()
        )

    @database_sync_to_async
    def update_selection(self, selection_range):
        """Update selection range in database."""
        from documents.models import DocumentSession

        DocumentSession.objects.filter(
            session_id=self.session_id
        ).update(
            selection_range=selection_range,
            last_activity_at=timezone.now()
        )

    @database_sync_to_async
    def update_activity(self):
        """Update last activity timestamp."""
        from documents.models import DocumentSession

        DocumentSession.objects.filter(
            session_id=self.session_id
        ).update(last_activity_at=timezone.now())

    @database_sync_to_async
    def save_operation(self, operation_data, base_version, sequence_number):
        """Save operation to database."""
        from documents.models import DocumentOperation, DocumentSession, Document

        document = Document.objects.get(id=self.document_id)
        session = DocumentSession.objects.get(session_id=self.session_id)

        DocumentOperation.objects.create(
            document=document,
            session=session,
            operation_type=operation_data.get('type'),
            operation_data=operation_data,
            base_version=base_version,
            sequence_number=sequence_number
        )

    @database_sync_to_async
    def get_active_sessions(self):
        """Get all active sessions for this document."""
        from documents.models import DocumentSession

        sessions = DocumentSession.objects.filter(
            document_id=self.document_id,
            is_active=True
        ).exclude(session_id=self.session_id).select_related('user')

        return [
            {
                'user_id': session.user.id,
                'user_email': session.user.email,
                'user_name': session.user.full_name,
                'session_id': session.session_id,
                'user_color': session.user_color,
                'cursor_position': session.cursor_position,
                'selection_range': session.selection_range,
            }
            for session in sessions
        ]

    def _generate_user_color(self):
        """Generate a color for the user's cursor."""
        colors = [
            '#3b82f6',  # blue
            '#10b981',  # green
            '#f59e0b',  # orange
            '#ef4444',  # red
            '#8b5cf6',  # purple
            '#ec4899',  # pink
            '#06b6d4',  # cyan
            '#f97316',  # orange-red
        ]
        # Use user ID to consistently assign same color
        return colors[self.user.id % len(colors)]

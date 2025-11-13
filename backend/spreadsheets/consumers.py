"""
WebSocket consumers for real-time spreadsheet collaboration.
Handles cell updates, cursor positions, and selections.
"""

import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class SpreadsheetCollaborationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time spreadsheet collaboration.
    Supports cell editing, cursor tracking, and cell selections.
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.spreadsheet_id = self.scope['url_route']['kwargs']['spreadsheet_id']
        self.room_group_name = f'spreadsheet_{self.spreadsheet_id}'
        self.user = self.scope['user']
        self.session_id = str(uuid.uuid4())

        # Assign a color for this user's selection
        self.user_color = self._generate_user_color()

        # Join spreadsheet room
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

        if message_type == 'cell_select':
            # Broadcast cell selection to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cell_selection',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'selected_cell': data.get('selected_cell'),
                }
            )
            # Update session in database
            await self.update_cell_selection(data.get('selected_cell'))

        elif message_type == 'range_select':
            # Broadcast range selection to other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'range_selection',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'selected_range': data.get('selected_range'),
                }
            )
            # Update session in database
            await self.update_range_selection(data.get('selected_range'))

        elif message_type == 'cell_update':
            # Handle cell value update
            cell_data = data.get('cell_data')
            base_version = data.get('base_version')
            sequence_number = data.get('sequence_number')

            # Save cell update to database
            await self.update_cell(cell_data)

            # Save operation for history
            await self.save_operation('cell_update', cell_data, base_version, sequence_number)

            # Broadcast to all other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cell_changed',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'cell_data': cell_data,
                    'base_version': base_version,
                    'sequence_number': sequence_number,
                }
            )

        elif message_type == 'format_update':
            # Handle cell formatting update
            format_data = data.get('format_data')
            base_version = data.get('base_version')
            sequence_number = data.get('sequence_number')

            # Save format update to database
            await self.update_cell_format(format_data)

            # Save operation for history
            await self.save_operation('format_update', format_data, base_version, sequence_number)

            # Broadcast to all other users
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'format_changed',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'format_data': format_data,
                    'base_version': base_version,
                    'sequence_number': sequence_number,
                }
            )

        elif message_type == 'row_insert':
            # Handle row insertion
            row_data = data.get('row_data')
            await self.save_operation('row_insert', row_data, data.get('base_version'), data.get('sequence_number'))

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'row_inserted',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'row_data': row_data,
                }
            )

        elif message_type == 'column_insert':
            # Handle column insertion
            column_data = data.get('column_data')
            await self.save_operation('column_insert', column_data, data.get('base_version'), data.get('sequence_number'))

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'column_inserted',
                    'user_id': self.user.id,
                    'session_id': self.session_id,
                    'column_data': column_data,
                }
            )

        elif message_type == 'sheet_change':
            # User switched to a different sheet
            sheet_id = data.get('sheet_id')
            await self.update_active_sheet(sheet_id)

            await self.send(text_data=json.dumps({
                'type': 'sheet_changed',
                'sheet_id': sheet_id
            }))

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

    async def cell_selection(self, event):
        """Send cell selection update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'cell_selection',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'selected_cell': event['selected_cell'],
            }))

    async def range_selection(self, event):
        """Send range selection update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'range_selection',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'selected_range': event['selected_range'],
            }))

    async def cell_changed(self, event):
        """Send cell update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'cell_changed',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'cell_data': event['cell_data'],
                'base_version': event['base_version'],
                'sequence_number': event['sequence_number'],
            }))

    async def format_changed(self, event):
        """Send format update to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'format_changed',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'format_data': event['format_data'],
                'base_version': event['base_version'],
                'sequence_number': event['sequence_number'],
            }))

    async def row_inserted(self, event):
        """Send row insertion to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'row_inserted',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'row_data': event['row_data'],
            }))

    async def column_inserted(self, event):
        """Send column insertion to WebSocket."""
        if event['session_id'] != self.session_id:
            await self.send(text_data=json.dumps({
                'type': 'column_inserted',
                'user_id': event['user_id'],
                'session_id': event['session_id'],
                'column_data': event['column_data'],
            }))

    # Database operations
    @database_sync_to_async
    def create_session(self):
        """Create a new spreadsheet session."""
        from spreadsheets.models import SpreadsheetSession, Spreadsheet

        spreadsheet = Spreadsheet.objects.get(id=self.spreadsheet_id)
        session = SpreadsheetSession.objects.create(
            spreadsheet=spreadsheet,
            user=self.user,
            session_id=self.session_id,
            user_color=self.user_color,
            is_active=True
        )
        return session.id

    @database_sync_to_async
    def deactivate_session(self):
        """Mark session as inactive."""
        from spreadsheets.models import SpreadsheetSession

        SpreadsheetSession.objects.filter(
            session_id=self.session_id
        ).update(is_active=False)

    @database_sync_to_async
    def update_cell_selection(self, selected_cell):
        """Update selected cell in database."""
        from spreadsheets.models import SpreadsheetSession

        SpreadsheetSession.objects.filter(
            session_id=self.session_id
        ).update(
            selected_cell=selected_cell,
            last_activity_at=timezone.now()
        )

    @database_sync_to_async
    def update_range_selection(self, selected_range):
        """Update selected range in database."""
        from spreadsheets.models import SpreadsheetSession

        SpreadsheetSession.objects.filter(
            session_id=self.session_id
        ).update(
            selected_range=selected_range,
            last_activity_at=timezone.now()
        )

    @database_sync_to_async
    def update_active_sheet(self, sheet_id):
        """Update active sheet in database."""
        from spreadsheets.models import SpreadsheetSession, Sheet

        sheet = Sheet.objects.get(id=sheet_id)
        SpreadsheetSession.objects.filter(
            session_id=self.session_id
        ).update(
            active_sheet=sheet,
            last_activity_at=timezone.now()
        )

    @database_sync_to_async
    def update_activity(self):
        """Update last activity timestamp."""
        from spreadsheets.models import SpreadsheetSession

        SpreadsheetSession.objects.filter(
            session_id=self.session_id
        ).update(last_activity_at=timezone.now())

    @database_sync_to_async
    def update_cell(self, cell_data):
        """Update cell value in database."""
        from spreadsheets.models import Cell, Sheet

        sheet_id = cell_data.get('sheet_id')
        row = cell_data.get('row')
        column = cell_data.get('column')
        value = cell_data.get('value')
        formula = cell_data.get('formula', '')
        data_type = cell_data.get('data_type', 'text')

        cell, created = Cell.objects.update_or_create(
            sheet_id=sheet_id,
            row=row,
            column=column,
            defaults={
                'value': value,
                'formula': formula,
                'data_type': data_type,
                'last_modified_by': self.user,
                'version': cell_data.get('version', 1),
            }
        )
        return cell.id

    @database_sync_to_async
    def update_cell_format(self, format_data):
        """Update cell formatting in database."""
        from spreadsheets.models import Cell

        sheet_id = format_data.get('sheet_id')
        row = format_data.get('row')
        column = format_data.get('column')
        format_config = format_data.get('format_config', {})

        Cell.objects.filter(
            sheet_id=sheet_id,
            row=row,
            column=column
        ).update(
            format_config=format_config,
            last_modified_by=self.user
        )

    @database_sync_to_async
    def save_operation(self, operation_type, operation_data, base_version, sequence_number):
        """Save operation to database for history."""
        from spreadsheets.models import SpreadsheetOperation, SpreadsheetSession, Spreadsheet

        spreadsheet = Spreadsheet.objects.get(id=self.spreadsheet_id)
        session = SpreadsheetSession.objects.get(session_id=self.session_id)

        SpreadsheetOperation.objects.create(
            spreadsheet=spreadsheet,
            session=session,
            operation_type=operation_type,
            operation_data=operation_data,
            base_version=base_version,
            sequence_number=sequence_number
        )

    @database_sync_to_async
    def get_active_sessions(self):
        """Get all active sessions for this spreadsheet."""
        from spreadsheets.models import SpreadsheetSession

        sessions = SpreadsheetSession.objects.filter(
            spreadsheet_id=self.spreadsheet_id,
            is_active=True
        ).exclude(session_id=self.session_id).select_related('user', 'active_sheet')

        return [
            {
                'user_id': session.user.id,
                'user_email': session.user.email,
                'user_name': session.user.full_name,
                'session_id': session.session_id,
                'user_color': session.user_color,
                'selected_cell': session.selected_cell,
                'selected_range': session.selected_range,
                'active_sheet_id': session.active_sheet_id,
            }
            for session in sessions
        ]

    def _generate_user_color(self):
        """Generate a color for the user's selection."""
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

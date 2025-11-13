"""
WebSocket consumers for real-time messaging.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Channel, ChannelMember, Message
from .serializers import MessageSerializer

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat.

    URL: ws://localhost:8000/ws/chat/{channel_id}/

    Message format:
    {
        "type": "message",
        "content": "Hello world",
        "parent_message_id": null  # Optional for threading
    }
    """

    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope['user']
        self.channel_id = self.scope['url_route']['kwargs']['channel_id']
        self.room_group_name = f'chat_{self.channel_id}'

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user has access to channel
        has_access = await self.check_channel_access()
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send online status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'status': 'online'
            }
        )

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Send offline status
        if hasattr(self, 'user') and self.user.is_authenticated:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'status': 'offline'
                }
            )

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'message')

            if message_type == 'message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing(data)
            elif message_type == 'reaction':
                await self.handle_reaction(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON'
            }))

    async def handle_chat_message(self, data):
        """Handle incoming chat message."""
        content = data.get('content', '').strip()
        parent_message_id = data.get('parent_message_id')

        if not content:
            return

        # Save message to database
        message = await self.save_message(content, parent_message_id)

        if message:
            # Serialize message
            message_data = await self.serialize_message(message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message_data
                }
            )

    async def handle_typing(self, data):
        """Handle typing indicator."""
        is_typing = data.get('is_typing', False)

        # Broadcast typing status to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'user_name': self.user.full_name,
                'is_typing': is_typing
            }
        )

    async def handle_reaction(self, data):
        """Handle message reaction."""
        message_id = data.get('message_id')
        emoji = data.get('emoji')

        if message_id and emoji:
            reaction_data = await self.toggle_reaction(message_id, emoji)

            if reaction_data:
                # Broadcast reaction to room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_reaction',
                        'message_id': message_id,
                        'reaction': reaction_data
                    }
                )

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))

    async def user_status(self, event):
        """Send user status to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'status': event['status']
        }))

    async def message_reaction(self, event):
        """Send message reaction to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'reaction': event['reaction']
        }))

    @database_sync_to_async
    def check_channel_access(self):
        """Check if user has access to channel."""
        try:
            channel = Channel.objects.get(id=self.channel_id)
            return ChannelMember.objects.filter(
                channel=channel,
                user=self.user
            ).exists()
        except Channel.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, parent_message_id=None):
        """Save message to database."""
        try:
            channel = Channel.objects.get(id=self.channel_id)

            parent_message = None
            if parent_message_id:
                try:
                    parent_message = Message.objects.get(
                        id=parent_message_id,
                        channel=channel
                    )
                except Message.DoesNotExist:
                    pass

            message = Message.objects.create(
                channel=channel,
                author=self.user,
                content=content,
                parent_message=parent_message,
                message_type=Message.TEXT
            )

            # Update thread count if reply
            if parent_message:
                parent_message.thread_reply_count += 1
                parent_message.save(update_fields=['thread_reply_count'])

            return message

        except Exception as e:
            print(f"Error saving message: {e}")
            return None

    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize message for JSON."""
        serializer = MessageSerializer(message)
        return serializer.data

    @database_sync_to_async
    def toggle_reaction(self, message_id, emoji):
        """Toggle reaction on message."""
        try:
            from .models import MessageReaction

            message = Message.objects.get(id=message_id, channel_id=self.channel_id)

            # Check if reaction exists
            reaction = MessageReaction.objects.filter(
                message=message,
                user=self.user,
                emoji=emoji
            ).first()

            if reaction:
                # Remove reaction
                reaction.delete()
                return {
                    'action': 'removed',
                    'user_id': self.user.id,
                    'emoji': emoji
                }
            else:
                # Add reaction
                MessageReaction.objects.create(
                    message=message,
                    user=self.user,
                    emoji=emoji
                )
                return {
                    'action': 'added',
                    'user_id': self.user.id,
                    'user_name': self.user.full_name,
                    'emoji': emoji
                }

        except Exception as e:
            print(f"Error toggling reaction: {e}")
            return None

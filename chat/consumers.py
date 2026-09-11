import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    """Handle WebSocket connections for the shared chat room."""

    async def connect(self):
        """Connect the user to the shared chat room."""
        self.room_group_name = 'EduApp_chat'

        if self.scope['user'].is_anonymous:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        messages = await self.get_chat_history()

        for chat_message in messages:
            await self.send(
                text_data=json.dumps(
                    {
                        'username': chat_message['username'],
                        'message': chat_message['message'],
                    }
                )
            )

    async def disconnect(self, close_code):
        """Remove the user from the chat room."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Receive a chat message and broadcast it."""
        data = json.loads(text_data)
        message = data.get('message', '').strip()

        if not message:
            return

        await self.save_message(message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username,
            }
        )

    async def chat_message(self, event):
        """Send a broadcast chat message to the browser."""
        await self.send(
            text_data=json.dumps(
                {
                    'message': event['message'],
                    'username': event['username'],
                }
            )
        )

    @database_sync_to_async
    def save_message(self, message):
        """Save a chat message to the database."""
        return ChatMessage.objects.create(
            user=self.scope['user'],
            message=message
        )

    @database_sync_to_async
    def get_chat_history(self):
        """Return recent chat messages from the database."""
        messages = ChatMessage.objects.select_related(
            'user'
        ).order_by(
            '-created_at'
        )[:50]

        return [
            {
                'username': message.user.username,
                'message': message.message,
            }
            for message in reversed(messages)
        ]
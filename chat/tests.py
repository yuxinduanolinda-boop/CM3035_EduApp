from django.contrib.auth.models import User
from django.test import TransactionTestCase, override_settings

from accounts.models import UserProfile
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator

from config.asgi import application

from .models import ChatMessage


@override_settings(
    CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer'
        }
    }
)
class ChatConsumerTest(TransactionTestCase):
    """Test the real-time WebSocket chat."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='chat_user',
            password='testpassword123'
        )

        UserProfile.objects.create(
            user=self.user,
            role='student',
            full_name='Chat User'
        )

    @database_sync_to_async
    def create_session(self):
        """Log the user in and return the session cookie."""
        self.client.force_login(self.user)
        return self.client.cookies['sessionid'].value

    async def create_communicator(self):
        """Create an authenticated WebSocket communicator."""
        session_id = await self.create_session()

        return WebsocketCommunicator(
            application,
            '/ws/chat/',
            headers=[
                (
                    b'cookie',
                    f'sessionid={session_id}'.encode()
                )
            ]
        )

    @database_sync_to_async
    def message_exists(self):
        """Check whether a chat message was saved."""
        return ChatMessage.objects.filter(
            user=self.user
        ).exists()

    async def test_authenticated_user_can_connect(self):
        """An authenticated user should connect successfully."""
        communicator = await self.create_communicator()

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.disconnect()

    async def test_anonymous_user_is_rejected(self):
        """An anonymous user should not be allowed to connect."""
        communicator = WebsocketCommunicator(
            application,
            '/ws/chat/'
        )

        connected, _ = await communicator.connect()

        self.assertFalse(connected)

        await communicator.disconnect()

    async def test_chat_message_is_saved_and_broadcast(self):
        """A chat message should be saved and sent back."""
        communicator = await self.create_communicator()

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                'message': 'Hello from the test.'
            }
        )

        response = await communicator.receive_json_from()

        self.assertEqual(
            response['username'],
            'chat_user'
        )

        self.assertEqual(
            response['message'],
            'Hello from the test.'
        )

        self.assertTrue(
            await self.message_exists()
        )

        await communicator.disconnect()

    async def test_empty_message_is_not_saved(self):
        """Empty chat messages should be ignored."""
        communicator = await self.create_communicator()

        connected, _ = await communicator.connect()

        self.assertTrue(connected)

        await communicator.send_json_to(
            {
                'message': '   '
            }
        )

        self.assertFalse(
            await self.message_exists()
        )

        await communicator.disconnect()
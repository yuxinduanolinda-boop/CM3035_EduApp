from django.contrib.auth.models import User
from django.db import models


class ChatMessage(models.Model):
    """Store a message sent through the chat."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.message[:30]}'
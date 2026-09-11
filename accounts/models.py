from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    full_name = models.CharField(max_length=100)

    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

class StatusUpdate(models.Model):
    """Store a status update posted by a user."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='status_updates'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:30]}'
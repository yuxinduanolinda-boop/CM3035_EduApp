from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serialize public user information."""

    full_name = serializers.SerializerMethodField(
        help_text='Full name from the user profile.'
    )

    role = serializers.SerializerMethodField(
        help_text='User role: student or teacher.'
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'full_name',
            'role',
        )
        extra_kwargs = {
            'username': {
                'help_text': 'Django username.'
            },
            'email': {
                'help_text': 'User email address.'
            },
        }

    def get_full_name(self, obj):
        """Return the profile full name."""
        if hasattr(obj, 'profile'):
            return obj.profile.full_name

        return ''

    def get_role(self, obj):
        """Return the profile role."""
        if hasattr(obj, 'profile'):
            return obj.profile.role

        return ''
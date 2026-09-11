from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Display notifications for the current user."""

    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        """Return only notifications belonging to the logged-in user."""
        return Notification.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
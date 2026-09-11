from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat_room(request):
    """Display the real-time chat page."""
    return render(
        request,
        'chat/chat.html'
    )
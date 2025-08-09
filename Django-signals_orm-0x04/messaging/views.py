
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model, logout
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
from .models import Message
@login_required
def unread_inbox(request):
    user = request.user
    unread_messages = Message.unread.unread_for_user(user)
    # Example: return as JSON (customize as needed for your UI)
    data = [
        {
            'id': msg.id,
            'sender': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp,
            'parent_message': msg.parent_message_id,
        }
        for msg in unread_messages
    ]
    return JsonResponse({'unread_messages': data})

User = get_user_model()

@login_required
@require_POST
def delete_user(request):
    user = request.user
    logout(request)
    user.delete()
    return HttpResponse("Your account and all related data have been deleted.")

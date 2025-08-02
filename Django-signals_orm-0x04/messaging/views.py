from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q
from .models import Message, Notification

@login_required
def inbox_unread(request):
    """Display unread messages using custom managers"""
    unread_messages = Message.unread.unread_for_user(request.user)
    unread_notifications = Notification.objects.unread_for_user(request.user)
    
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
        'unread_count': unread_messages.count(),
        'notification_count': unread_notifications.count()
    })

@login_required
def conversation_view(request, message_id):
    """View conversation thread"""
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver').only(
            'id', 'content', 'timestamp', 'sender__username', 
            'receiver__username', 'read', 'parent_message_id'
        ),
        Q(id=message_id),
        Q(sender=request.user) | Q(receiver=request.user)
    )
    message.mark_as_read()
    
    thread_messages = Message.objects.get_conversation(message)
    
    messages_dict = {m.id: {'message': m, 'replies': []} for m in thread_messages}
    thread_structure = []
    
    for m in thread_messages:
        if m.parent_message:
            messages_dict[m.parent_message.id]['replies'].append(messages_dict[m.id])
        else:
            thread_structure.append(messages_dict[m.id])

    return render(request, 'messaging/conversation.html', {
        'root_message': message,
        'thread_structure': thread_structure,
        'current_user': request.user
    })

@login_required
def delete_user(request):
    """Handle user account deletion"""
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
    return render(request, 'messaging/confirm_delete.html')

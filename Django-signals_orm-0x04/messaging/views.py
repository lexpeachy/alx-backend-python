from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import Message, Notification

@login_required
def inbox_unread(request):
    """View for displaying unread messages and notifications"""
    unread_messages = Message.unread.for_user(request.user)
    unread_notifications = Notification.objects.filter(
        user=request.user,
        read=False
    ).select_related('message__sender')
    
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_notifications': unread_notifications,
        'unread_count': unread_messages.count(),
        'notification_count': unread_notifications.count()
    })

@login_required
def conversation_view(request, message_id):
    """View for displaying threaded conversations"""
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        Q(id=message_id),
        Q(sender=request.user) | Q(receiver=request.user)
    )
    
    # Mark message and its notifications as read
    message.mark_as_read()
    
    # Find root message
    root_message = message
    while root_message.parent_message:
        root_message = root_message.parent_message

    # Get all messages in the thread
    thread_messages = Message.objects.filter(
        Q(id=root_message.id) | 
        Q(parent_message=root_message.id) |
        Q(parent_message__parent_message=root_message.id)
    ).select_related(
        'sender', 'receiver', 'parent_message'
    ).order_by('timestamp')

    # Build thread structure
    messages_dict = {m.id: {'message': m, 'replies': []} for m in thread_messages}
    thread_structure = []
    
    for m in thread_messages:
        if m.parent_message:
            messages_dict[m.parent_message.id]['replies'].append(messages_dict[m.id])
        else:
            thread_structure.append(messages_dict[m.id])

    return render(request, 'messaging/conversation.html', {
        'root_message': root_message,
        'thread_structure': thread_structure,
        'current_user': request.user
    })

@login_required
def notifications_view(request):
    """View for displaying all notifications"""
    notifications = Notification.objects.filter(
        user=request.user
    ).select_related(
        'message', 'message__sender'
    ).order_by('-created_at')
    
    return render(request, 'messaging/notifications.html', {
        'notifications': notifications
    })

@login_required
def mark_notification_read(request, notification_id):
    """View to mark a notification as read"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.mark_as_read()
    return redirect(request.META.get('HTTP_REFERER', 'notifications'))

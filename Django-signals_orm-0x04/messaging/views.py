from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message

@login_required
def inbox_unread(request):
    """View for displaying unread messages"""
    unread_messages = Message.unread.for_user(request.user)
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_messages.count()
    })

@login_required
def conversation_view(request, message_id):
    """View for displaying threaded conversations"""
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        Q(id=message_id),
        Q(sender=request.user) | Q(receiver=request.user)
    )
    
    # Mark message as read when viewed
    message.mark_as_read()
    
    # Find root message
    root_message = message
    while root_message.parent_message:
        root_message = root_message.parent_message

    # Recursive query to build thread
    def get_thread_messages(message):
        messages = []
        full_message = Message.objects.filter(id=message.id).select_related(
            'sender', 'receiver', 'parent_message'
        ).first()
        if full_message:
            messages.append(full_message)
            replies = Message.objects.filter(parent_message=full_message).select_related(
                'sender', 'receiver', 'parent_message'
            )
            for reply in replies:
                messages.extend(get_thread_messages(reply))
        return messages

    thread_messages = get_thread_messages(root_message)

    # Build thread structure
    def build_thread_structure(messages):
        message_dict = {m.id: {'message': m, 'replies': []} for m in messages}
        thread_structure = []
        for m in messages:
            if m.parent_message:
                message_dict[m.parent_message.id]['replies'].append(message_dict[m.id])
            else:
                thread_structure.append(message_dict[m.id])
        return thread_structure

    return render(request, 'messaging/conversation.html', {
        'root_message': root_message,
        'thread_structure': build_thread_structure(thread_messages),
        'current_user': request.user
    })

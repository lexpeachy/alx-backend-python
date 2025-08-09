
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message

@login_required
def conversation_view(request, message_id):
    # Get the initial message with optimized queries
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        Q(id=message_id),
        Q(sender=request.user) | Q(receiver=request.user)
    )

    # Find the root message of the thread
    root_message = message
    while root_message.parent_message:
        root_message = root_message.parent_message

    # Recursive query to get all messages in the thread
    def get_thread_messages(message):
        messages = []
        # Get the message with all related data
        full_message = Message.objects.filter(id=message.id).select_related(
            'sender', 'receiver', 'parent_message'
        ).first()
        if full_message:
            messages.append(full_message)
            # Get all replies recursively
            replies = Message.objects.filter(parent_message=full_message).select_related(
                'sender', 'receiver', 'parent_message'
            )
            for reply in replies:
                messages.extend(get_thread_messages(reply))
        return messages

    # Get all messages in the thread
    thread_messages = get_thread_messages(root_message)

    # Build the thread structure for template rendering
    def build_thread_structure(messages):
        message_dict = {m.id: {'message': m, 'replies': []} for m in messages}
        thread_structure = []
        
        for m in messages:
            if m.parent_message:
                message_dict[m.parent_message.id]['replies'].append(message_dict[m.id])
            else:
                thread_structure.append(message_dict[m.id])
        return thread_structure

    thread_structure = build_thread_structure(thread_messages)

    return render(request, 'messaging/conversation.html', {
        'root_message': root_message,
        'thread_structure': thread_structure,
        'current_user': request.user
    })
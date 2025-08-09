from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """Model to store notifications for users about new messages"""
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey('Message', related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username} about message {self.message.id}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.read:
            self.read = True
            self.save()

class MessageManager(models.Manager):
    def get_conversation(self, message):
        """Get entire conversation thread starting from a message"""
        return self.filter(
            models.Q(id=message.id) |
            models.Q(parent_message=message.id) |
            models.Q(parent_message__parent_message=message.id)
        ).select_related('sender', 'receiver', 'parent_message')

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        return self.get_queryset().filter(receiver=user, read=False).only('id', 'sender', 'content', 'timestamp', 'parent_message')

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(null=True, blank=True)  # Track when message was edited
    parent_message = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)

    objects = models.Manager()  # Default manager
    unread = UnreadMessagesManager()  # Custom manager for unread messages

    def __str__(self):
        return f"From {self.sender} to {self.receiver}: {self.content[:20]}"

    def get_thread(self):
        """
        Recursively fetch all replies to this message in a threaded structure.
        Returns a list of dicts with message and its replies.
        """
        def fetch_replies(message):
            replies = message.replies.select_related('sender', 'receiver').all()
            return [
                {
                    'message': reply,
                    'replies': fetch_replies(reply)
                }
                for reply in replies
            ]
        return fetch_replies(self)

    def get_edit_history(self):
        """Returns all edit history for this message"""
        return self.history.all().order_by('-edited_at')

class MessageHistory(models.Model):
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    content = models.TextField()  # Old content before edit
    edited_at = models.DateTimeField(auto_now_add=True)  # When this version was saved
    
    class Meta:
        ordering = ['-edited_at']
        verbose_name_plural = 'Message Histories'
    
    def __str__(self):
        return f"History for message {self.message.id} ({self.edited_at})"

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    """
    Signal handler to track message edits and save previous versions.
    """
    if instance.pk:  # Only for existing messages (not new ones)
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content has changed
                # Save old version to history
                MessageHistory.objects.create(
                    message=old_message,
                    content=old_message.content
                )
                # Update edited timestamp
                instance.edited = timezone.now()
        except Message.DoesNotExist:
            pass  # Message was deleted or doesn't exist

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user} about message {self.message.id}"

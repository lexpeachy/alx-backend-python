from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.conf import settings
from .models import Message, Notification, MessageHistory
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    """Track message edits and save previous versions to MessageHistory"""
    if instance.pk and not kwargs.get('raw', False):  # Existing message being updated
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:  # Content changed
                # Save old version to history
                MessageHistory.objects.create(
                    message=old_message,
                    content=old_message.content,
                    edited_by=instance.sender  # Track who made the edit
                )
                # Update edited fields
                instance.edited = timezone.now()
                instance.edited_by = instance.sender
        except Message.DoesNotExist:
            pass

@receiver(post_delete, sender=User)
def delete_related_data_on_user_delete(sender, instance, **kwargs):
    # Delete all messages sent by the user
    Message.objects.filter(sender=instance).delete()
    
    # Delete all messages received by the user
    Message.objects.filter(receiver=instance).delete()
    
    # Delete all notifications for the user
    Notification.objects.filter(user=instance).delete()
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Message, Notification
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(pre_save, sender=Message)
def track_message_edit(sender, instance, **kwargs):
    """Track message edits and save previous versions to MessageHistory"""
    if instance.pk and not kwargs.get('raw', False):
        try:
            old_message = Message.objects.get(pk=instance.pk)
            if old_message.content != instance.content:
                MessageHistory.objects.create(
                    message=old_message,
                    content=old_message.content,
                    edited_by=instance.sender
                )
                instance.edited = timezone.now()
                instance.edited_by = instance.sender
        except Message.DoesNotExist:
            pass

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    """Create notification when new message is sent"""
    if created and instance.receiver != instance.sender:  # Don't notify yourself
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


# Clean up related data when a user is deleted (if not handled by CASCADE)
@receiver(post_delete, sender=User)
def delete_related_data_on_user_delete(sender, instance, **kwargs):
    # Messages and Notifications are already set to CASCADE, but if you add more related models, clean up here
    pass

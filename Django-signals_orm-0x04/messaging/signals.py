from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import Message, Notification
from django.contrib.auth import get_user_model
User = get_user_model()

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.receiver,
            message=instance
        )


# Clean up related data when a user is deleted (if not handled by CASCADE)
@receiver(post_delete, sender=User)
def delete_related_data_on_user_delete(sender, instance, **kwargs):
    # Messages and Notifications are already set to CASCADE, but if you add more related models, clean up here
    pass

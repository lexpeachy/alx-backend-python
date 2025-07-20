import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser with additional fields.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="User ID"
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        blank=False,
        null=False
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True
    )
    first_name = models.CharField(
        _('first name'),
        max_length=150,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
        blank=False,
        null=False
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )
    online_status = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)

class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Conversation ID"
    )
    participants = models.ManyToManyField(
        User,
        related_name='conversations'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group_chat = models.BooleanField(default=False)
    name = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.is_group_chat and self.name:
            return f"Group: {self.name}"
        return f"Conversation ({self.conversation_id})"

class Message(models.Model):
    """
    Model representing a message in a conversation.
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Message ID"
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    message_body = models.TextField(
        help_text="The content of the message"
    )
    sent_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was sent"
    )
    read_by = models.ManyToManyField(
        User,
        related_name='read_messages',
        blank=True
    )
    
    class Meta:
        ordering = ['sent_at']
    
    def __str__(self):
        return f"Message {self.message_id} from {self.sender}"
    
    def mark_as_read(self, user):
        """
        Mark the message as read by a specific user.
        """
        if user not in self.read_by.all():
            self.read_by.add(user)
            self.conversation.updated_at = timezone.now()
            self.conversation.save()
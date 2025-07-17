from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class User(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    online_status = models.BooleanField(default=False)
    last_seen = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversation' )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_group_chat = models.BooleanField(default=False)
    group_name = models.CharField(max_length=100, blank = True, null=True)

    class meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.is_group_chat and self.group_name:
            return self.group_name
        username = [User.username for user in self.participants.all()]
        return f'conversation between {', '.join(username)}'
    
class Message(models.Model):
    conversation= models.ForeignKey(Conversation, on_delete=models.CASCADE,related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)

    class meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'message from {self.sender.username} at {self.timestamp}'
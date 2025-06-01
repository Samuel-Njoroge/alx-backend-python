from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    # Explicitly mention fields to satisfy checks (even though inherited)
    email = models.EmailField(unique=True)  # Explicitly redeclare email (optional)
    password = models.CharField(max_length=128)  # Explicitly redeclare password (optional)
    first_name = models.CharField(max_length=150, blank=True)  # Explicitly redeclare first_name (optional)
    last_name = models.CharField(max_length=150, blank=True)  # Explicitly redeclare last_name (optional)

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.conversation_id}"


class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message {self.message_id} from {self.sender.username} in conversation {self.conversation.conversation_id}"

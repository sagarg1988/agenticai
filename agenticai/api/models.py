from django.db import models
from django.contrib.auth.models import User
import uuid

class AgentSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)
    metadata = models.JSONField(default=dict)

class ConversationMessage(models.Model):
    session = models.ForeignKey(AgentSession, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=16, choices=[("user","user"),("assistant","assistant"),("system","system")])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tokens = models.IntegerField(null=True, blank=True)

class LongTermMemory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AgentSession, null=True, blank=True, on_delete=models.SET_NULL)
    text = models.TextField()
    vector_id = models.CharField(max_length=128, null=True, blank=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=512)
    source = models.CharField(max_length=512, null=True, blank=True)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

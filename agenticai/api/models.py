"""
API models for AgenticAI platform.

Core entities:
- Agent: a named AI agent configuration
- AgentRun: a single execution run of an agent
- Message: a chat message within a run
"""
import uuid

from django.db import models


class Agent(models.Model):
    """Represents a configured AI agent."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    system_prompt = models.TextField(blank=True)
    tools = models.JSONField(default=list, help_text="List of enabled tool names")
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name


class AgentRun(models.Model):
    """Represents a single execution run of an agent."""

    class State(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, related_name="runs")
    input = models.TextField()
    output = models.TextField(blank=True)
    state = models.CharField(
        max_length=20, choices=State.choices, default=State.PENDING
    )
    error = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.agent.name} run {self.id}"


class Message(models.Model):
    """A message in the conversation of an agent run."""

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"
        SYSTEM = "system", "System"
        TOOL = "tool", "Tool"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.ForeignKey(
        AgentRun, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=20, choices=Role.choices)
    content = models.TextField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"[{self.role}] {self.content[:60]}"

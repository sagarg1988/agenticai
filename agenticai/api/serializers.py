"""Serializers for AgenticAI API."""
from rest_framework import serializers

from .models import Agent, AgentRun, Message


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = [
            "id",
            "name",
            "description",
            "system_prompt",
            "tools",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "role", "content", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]


class AgentRunSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = AgentRun
        fields = [
            "id",
            "agent",
            "input",
            "output",
            "state",
            "error",
            "metadata",
            "messages",
            "started_at",
            "finished_at",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "output",
            "state",
            "error",
            "messages",
            "started_at",
            "finished_at",
            "created_at",
        ]


class AgentRunCreateSerializer(serializers.ModelSerializer):
    """Lightweight serializer for creating a new run."""

    class Meta:
        model = AgentRun
        fields = ["agent", "input", "metadata"]

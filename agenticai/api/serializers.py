"""DRF serializers for AgenticAI API."""

from rest_framework import serializers

from .models import Agent, AgentRun


class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agent
        fields = ["id", "name", "description", "tool_config", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class AgentRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentRun
        fields = [
            "id",
            "agent",
            "input_data",
            "output_data",
            "status",
            "error",
            "started_at",
            "finished_at",
            "created_at",
        ]
        read_only_fields = ["id", "output_data", "status", "error", "started_at", "finished_at", "created_at"]


class AgentRunRequestSerializer(serializers.Serializer):
    """Payload for triggering a new agent run."""

    # TODO: add strict input schema validation per agent type
    input_data = serializers.DictField(default=dict)

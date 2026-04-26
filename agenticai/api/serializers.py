from rest_framework import serializers
from .models import AgentSession, ConversationMessage, LongTermMemory

class AgentSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentSession
        fields = "__all__"

class ConversationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationMessage
        fields = "__all__"

class LongTermMemorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LongTermMemory
        fields = "__all__"

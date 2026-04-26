"""Admin registration for AgenticAI models."""
from django.contrib import admin

from .models import Agent, AgentRun, Message


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["name", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["name", "description"]


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ["id", "agent", "state", "created_at"]
    list_filter = ["state"]
    search_fields = ["agent__name"]
    readonly_fields = ["id", "created_at", "started_at", "finished_at"]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "run", "role", "created_at"]
    list_filter = ["role"]
    readonly_fields = ["id", "created_at"]

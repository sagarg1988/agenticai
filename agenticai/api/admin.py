"""Django admin registrations for AgenticAI API."""

from django.contrib import admin

from .models import Agent, AgentRun


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at", "updated_at"]
    search_fields = ["name"]


@admin.register(AgentRun)
class AgentRunAdmin(admin.ModelAdmin):
    list_display = ["agent", "status", "created_at", "started_at", "finished_at"]
    list_filter = ["status"]
    readonly_fields = ["output_data", "error", "started_at", "finished_at"]

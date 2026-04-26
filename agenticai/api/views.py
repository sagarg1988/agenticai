"""API views for AgenticAI platform."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Agent, AgentRun
from .serializers import (
    AgentRunCreateSerializer,
    AgentRunSerializer,
    AgentSerializer,
)


class AgentViewSet(viewsets.ModelViewSet):
    """CRUD operations for Agent configurations."""

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer


class AgentRunViewSet(viewsets.ModelViewSet):
    """Manage agent run lifecycle."""

    queryset = AgentRun.objects.select_related("agent").prefetch_related("messages")
    serializer_class = AgentRunSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return AgentRunCreateSerializer
        return AgentRunSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        run = serializer.save()

        # TODO: dispatch Celery task to execute the run asynchronously
        # from celery_tasks.tasks import execute_agent_run
        # execute_agent_run.delay(str(run.id))

        headers = self.get_success_headers(serializer.data)
        return Response(
            AgentRunSerializer(run).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a pending or running agent run."""
        run = self.get_object()
        if run.state not in (AgentRun.State.PENDING, AgentRun.State.RUNNING):
            return Response(
                {"detail": "Run is not cancellable."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        run.state = AgentRun.State.FAILED
        run.error = "Cancelled by user."
        run.save(update_fields=["state", "error"])
        return Response(AgentRunSerializer(run).data)

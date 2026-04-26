"""API views for AgenticAI platform."""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from agenticai.celery_tasks.tasks import run_agent_task

from .models import Agent, AgentRun
from .serializers import AgentRunRequestSerializer, AgentRunSerializer, AgentSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """CRUD operations for Agent resources."""

    queryset = Agent.objects.all()
    serializer_class = AgentSerializer

    @action(detail=True, methods=["post"])
    def run(self, request, pk=None):
        """Enqueue an agent run via Celery."""
        agent = self.get_object()
        req_serializer = AgentRunRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        agent_run = AgentRun.objects.create(
            agent=agent,
            input_data=req_serializer.validated_data["input_data"],
        )

        # Dispatch async task
        # TODO: add rate limiting / concurrency controls per agent
        run_agent_task.delay(str(agent_run.id))

        serializer = AgentRunSerializer(agent_run)
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)


class AgentRunViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only view of agent run history."""

    queryset = AgentRun.objects.select_related("agent").all()
    serializer_class = AgentRunSerializer

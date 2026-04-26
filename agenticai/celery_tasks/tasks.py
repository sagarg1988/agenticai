"""
Celery tasks for AgenticAI platform.

TODO: add task routing to dedicated queues (e.g., high-priority, background).
TODO: add dead-letter queue / error alerting for failed tasks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from celery import Celery

from agenticai.agents.runner import AgentRunner

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Celery application
# ---------------------------------------------------------------------------
import os

celery_app = Celery(
    "agenticai",
    broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
)
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------
@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def run_agent_task(self, run_id: str) -> dict:
    """
    Execute an AgentRun asynchronously.

    Imports are inside the function to avoid circular imports at module load time.
    TODO: add idempotency guard — check if run is already in RUNNING state.
    """
    # Import here to avoid circular imports
    from agenticai.api.models import AgentRun  # noqa: PLC0415

    try:
        run = AgentRun.objects.select_related("agent").get(pk=run_id)
    except AgentRun.DoesNotExist:
        logger.error("run_agent_task: AgentRun not found", extra={"run_id": run_id})
        return {"error": "AgentRun not found"}

    run.status = AgentRun.Status.RUNNING
    run.started_at = datetime.now(tz=timezone.utc)
    run.save(update_fields=["status", "started_at"])

    try:
        runner = AgentRunner()
        result = runner.run(
            goal=run.input_data.get("goal", ""),
            context=run.input_data,
        )
        run.output_data = result
        run.status = AgentRun.Status.SUCCESS
        run.finished_at = datetime.now(tz=timezone.utc)
        run.save(update_fields=["status", "output_data", "error", "finished_at"])
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_agent_task failed", extra={"run_id": run_id})
        run.error = str(exc)
        run.status = AgentRun.Status.FAILURE
        run.finished_at = datetime.now(tz=timezone.utc)
        run.save(update_fields=["status", "output_data", "error", "finished_at"])
        # TODO: decide whether to retry on transient errors only
        raise self.retry(exc=exc)

    return {"run_id": run_id, "status": run.status}

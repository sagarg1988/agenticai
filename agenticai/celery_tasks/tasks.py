"""
Celery tasks for AgenticAI platform.

TODO:
- Add task routing (separate queues for fast/slow tasks).
- Configure task retry policies and dead-letter queues.
- Emit task events to the observability stack.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=5)
def execute_agent_run(self, run_id: str) -> dict:
    """
    Execute an AgentRun asynchronously.

    Args:
        run_id: UUID string of the AgentRun to execute.

    Returns:
        Dict with run_id and final state.
    """
    # Import inside task to avoid app-not-ready errors at import time
    from api.models import Agent, AgentRun  # noqa: PLC0415
    from agents.runner import AgentRunner  # noqa: PLC0415

    logger.info("execute_agent_run run_id=%s", run_id)

    try:
        run = AgentRun.objects.select_related("agent").get(id=run_id)
    except AgentRun.DoesNotExist:
        logger.error("AgentRun %s not found", run_id)
        return {"run_id": run_id, "state": "not_found"}

    run.state = AgentRun.State.RUNNING
    run.started_at = datetime.now(tz=timezone.utc)
    run.save(update_fields=["state", "started_at"])

    try:
        agent_config = {
            "name": run.agent.name,
            "system_prompt": run.agent.system_prompt,
            "tools": run.agent.tools,
        }
        runner = AgentRunner(agent_config)
        output = runner.run(run.input)

        run.output = output
        run.state = AgentRun.State.COMPLETED
    except Exception as exc:  # noqa: BLE001
        logger.exception("AgentRun %s failed: %s", run_id, exc)
        run.state = AgentRun.State.FAILED
        run.error = str(exc)
        # Retry on transient failures
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error("Max retries exceeded for run %s", run_id)
    finally:
        run.finished_at = datetime.now(tz=timezone.utc)
        run.save(update_fields=["output", "state", "error", "finished_at"])

    return {"run_id": run_id, "state": run.state}

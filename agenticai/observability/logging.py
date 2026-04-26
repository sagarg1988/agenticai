"""
Structured logging configuration for AgenticAI platform.

Uses structlog for JSON-formatted, context-rich log output suitable for
ingestion into Datadog, Elastic, or any log aggregation backend.

TODO:
- Add OpenTelemetry trace / span context injection.
- Configure log level via environment variable.
- Add Sentry integration for exception tracking in production.
"""
from __future__ import annotations

import logging
import sys

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structlog and stdlib logging for the application.

    Call once at startup (e.g., in settings or WSGI/ASGI app init).
    """
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # Final renderer: JSON in production, coloured in dev
        # TODO: switch to JSON renderer (structlog.processors.JSONRenderer)
        #       when LOG_FORMAT=json env var is set
        processor=structlog.dev.ConsoleRenderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

"""Celery application instance for AgenticAI."""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aiagent.settings.base")

app = Celery("aiagent")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

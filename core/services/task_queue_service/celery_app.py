"""
Celery app - configuração central Core_SinapUm.
Filas: events_ingest, domain_processing, ai_calls, metrics_batch, webhooks_out
"""
from celery import Celery
from kombu import Queue
import os

REDIS_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

app = Celery("core_sinapum")
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=RESULT_BACKEND,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=60,
    task_max_retries=5,
    task_routes={
        "core.services.task_queue_service.tasks.ingest_event": {"queue": "events_ingest"},
        "core.services.task_queue_service.tasks.process_inbound_event": {"queue": "events_ingest"},
        "core.services.task_queue_service.tasks.domain_process": {"queue": "domain_processing"},
        "core.services.task_queue_service.tasks.webhook_out": {"queue": "webhooks_out"},
        "core.services.task_queue_service.tasks.metrics_batch": {"queue": "metrics_batch"},
    },
    task_queues=(
        Queue("events_ingest"),
        Queue("domain_processing"),
        Queue("ai_calls"),
        Queue("metrics_batch"),
        Queue("webhooks_out"),
    ),
)

# Autodiscover tasks em apps do Django (setup) e em core.services.task_queue_service
try:
    from django.conf import settings
    app.config_from_object("django.conf:settings", namespace="CELERY")
except Exception:
    pass
app.autodiscover_tasks(["core.services.task_queue_service"])

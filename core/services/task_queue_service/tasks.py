import json
import time
from typing import Any, Dict

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from app_inbound_events.models import InboundEvent, InboundEventStatus
from .idempotency import redis_lock, idempotency_key
from .flow import run_event_flow


def _safe_json(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    try:
        return json.loads(payload)
    except Exception:
        return {"raw": str(payload)}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def ingest_event(self, event_id: str, source: str, payload: Any) -> str:
    payload_json = _safe_json(payload)
    obj, created = InboundEvent.objects.get_or_create(
        event_id=event_id,
        defaults={
            "source": source,
            "payload_json": payload_json,
            "status": InboundEventStatus.RECEIVED,
        },
    )
    if obj.status in {InboundEventStatus.RECEIVED, InboundEventStatus.FAILED}:
        obj.status = InboundEventStatus.ENQUEUED
        obj.error_message = ""
        obj.save(update_fields=["status", "error_message"])
        process_inbound_event.delay(event_id)
    return event_id


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def process_inbound_event(self, event_id: str) -> str:
    lock_key = idempotency_key(event_id)
    with redis_lock(lock_key, ttl_seconds=180, wait_seconds=0) as acquired:
        if not acquired:
            return event_id
        with transaction.atomic():
            ev = InboundEvent.objects.select_for_update().get(event_id=event_id)
            if ev.status == InboundEventStatus.PROCESSED:
                return event_id
            ev.status = InboundEventStatus.PROCESSING
            ev.save(update_fields=["status"])
        try:
            run_event_flow(inbound_event_id=event_id)
            with transaction.atomic():
                ev = InboundEvent.objects.select_for_update().get(event_id=event_id)
                ev.status = InboundEventStatus.PROCESSED
                ev.processed_at = timezone.now()
                ev.error_message = ""
                ev.save(update_fields=["status", "processed_at", "error_message"])
        except Exception as e:
            with transaction.atomic():
                ev = InboundEvent.objects.select_for_update().get(event_id=event_id)
                ev.status = InboundEventStatus.FAILED
                ev.error_message = str(e)[:5000]
                ev.save(update_fields=["status", "error_message"])
            raise
    return event_id

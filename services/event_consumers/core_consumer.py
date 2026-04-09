#!/usr/bin/env python3
"""
Core Consumer - Consumidor de eventos WhatsApp para Core_SinapUm

Processa eventos whatsapp.inbound e encaminha para:
- app_whatsapp_events (roteamento, canonical events)
- webhook legado (se configurado)
"""
import json
import logging
import os
import sys

# Adicionar Core_SinapUm ao path
CORE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if CORE_ROOT not in sys.path:
    sys.path.insert(0, CORE_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "setup.settings")

import django
django.setup()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
STREAM = "whatsapp.inbound"
CONSUMER_GROUP = "event_consumers"
CONSUMER_NAME = "core_consumer"


def handle_event(data: dict):
    """Processa evento WhatsApp recebido"""
    event = data.get("event", "")
    instance_id = data.get("instance_id", "default")
    payload = data.get("payload", {})

    logger.info(f"[Core] Event {event} instance={instance_id}")

    try:
        # Encaminhar para webhook interno do Core (Django)
        from django.conf import settings
        webhook_url = getattr(settings, "SINAPUM_WHATSAPP_WEBHOOK_URL", None)
        if webhook_url:
            import requests
            resp = requests.post(
                webhook_url,
                json={
                    "instance_id": instance_id,
                    "event_type": event.replace("whatsapp.", ""),
                    "payload": payload,
                    "ts": data.get("timestamp", ""),
                },
                headers={"X-API-Key": os.environ.get("SINAPUM_WHATSAPP_GATEWAY_API_KEY", "")},
                timeout=10,
            )
            if resp.status_code != 200:
                logger.warning(f"Webhook returned {resp.status_code}")
    except Exception as e:
        logger.error(f"Error processing event: {e}", exc_info=True)


def main():
    # Adicionar event_bus_service ao path
    event_bus_path = os.path.join(CORE_ROOT, "services", "event_bus_service")
    if event_bus_path not in sys.path:
        sys.path.insert(0, event_bus_path)

    from event_bus.consumer import EventBusConsumer

    consumer = EventBusConsumer(
        redis_url=REDIS_URL,
        stream=STREAM,
        consumer_name=CONSUMER_NAME,
        handler=handle_event,
    )
    consumer.run()


if __name__ == "__main__":
    main()

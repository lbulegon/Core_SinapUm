#!/usr/bin/env python3
"""
Evora Consumer - Consumidor de eventos WhatsApp para VitrineZap/Evora

Deve rodar no contexto do Evora (Railway) ou como serviço que chama Evora.
Processa eventos whatsapp.inbound e encaminha para EVORA_WHATSAPP_WEBHOOK_URL.
"""
import json
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
EVORA_WEBHOOK_URL = os.environ.get("EVORA_WHATSAPP_WEBHOOK_URL", "")
STREAM = "whatsapp.inbound"
CONSUMER_GROUP = "event_consumers"
CONSUMER_NAME = "evora_consumer"


def handle_event(data: dict):
    """Encaminha evento para webhook do Evora"""
    if not EVORA_WEBHOOK_URL:
        logger.debug("EVORA_WHATSAPP_WEBHOOK_URL not configured, skipping")
        return

    event = data.get("event", "")
    instance_id = data.get("instance_id", "default")
    payload = data.get("payload", {})

    logger.info(f"[Evora] Forwarding {event} instance={instance_id}")

    try:
        import requests
        resp = requests.post(
            EVORA_WEBHOOK_URL,
            json={
                "instance_id": instance_id,
                "event_type": event.replace("whatsapp.", ""),
                "payload": payload,
                "ts": data.get("timestamp", ""),
            },
            timeout=10,
        )
        if resp.status_code != 200:
            logger.warning(f"Evora webhook returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logger.error(f"Error forwarding to Evora: {e}", exc_info=True)


def main():
    # Import do consumer - requer event_bus_service no path
    event_bus_path = os.environ.get(
        "EVENT_BUS_SERVICE_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../event_bus_service"))
    )
    if os.path.exists(event_bus_path) and event_bus_path not in sys.path:
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

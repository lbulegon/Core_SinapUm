#!/usr/bin/env python3
"""
ShopperBot Consumer - Consumidor de eventos WhatsApp para ShopperBot

Processa mensagens recebidas e encaminha para o ShopperBot quando aplicável.
"""
import logging
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
SHOPPERBOT_WEBHOOK_URL = os.environ.get("SHOPPERBOT_WHATSAPP_WEBHOOK_URL", "")
STREAM = "whatsapp.inbound"
CONSUMER_GROUP = "event_consumers"
CONSUMER_NAME = "shopperbot_consumer"


def handle_event(data: dict):
    """Encaminha mensagens para ShopperBot"""
    if not SHOPPERBOT_WEBHOOK_URL:
        logger.debug("SHOPPERBOT_WHATSAPP_WEBHOOK_URL not configured, skipping")
        return

    event = data.get("event", "")
    if event != "whatsapp.message.received":
        return  # ShopperBot só processa mensagens

    instance_id = data.get("instance_id", "default")
    payload = data.get("payload", {})

    logger.info(f"[ShopperBot] Forwarding message instance={instance_id}")

    try:
        import requests
        resp = requests.post(
            SHOPPERBOT_WEBHOOK_URL,
            json={
                "instance_id": instance_id,
                "event_type": "message",
                "payload": payload,
                "ts": data.get("timestamp", ""),
            },
            timeout=10,
        )
        if resp.status_code != 200:
            logger.warning(f"ShopperBot webhook returned {resp.status_code}")
    except Exception as e:
        logger.error(f"Error forwarding to ShopperBot: {e}", exc_info=True)


def main():
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

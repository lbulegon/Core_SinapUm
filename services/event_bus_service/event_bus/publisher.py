"""
Event Bus Publisher - Publica eventos em Redis Streams
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import redis

logger = logging.getLogger(__name__)

# Streams (tópicos)
STREAM_WHATSAPP_INBOUND = "whatsapp.inbound"
STREAM_WHATSAPP_OUTBOUND = "whatsapp.outbound"
STREAM_LEADS_CAPTURED = "leads.captured"
STREAM_ORDERS_CREATED = "orders.created"


class EventBusPublisher:
    """Publica eventos em Redis Streams"""

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def _stream_for_event(self, event: str) -> str:
        """Mapeia evento para stream"""
        if event.startswith("whatsapp.message") or event in ("whatsapp.qr", "whatsapp.connected", "whatsapp.disconnected"):
            return STREAM_WHATSAPP_INBOUND
        if event.startswith("whatsapp.sent"):
            return STREAM_WHATSAPP_OUTBOUND
        if event.startswith("lead."):
            return STREAM_LEADS_CAPTURED
        if event.startswith("order."):
            return STREAM_ORDERS_CREATED
        return "events.general"

    def publish(
        self,
        event: str,
        payload: Dict[str, Any],
        instance_id: str = "default",
        jid: Optional[str] = None,
        source: str = "unknown",
    ) -> Optional[str]:
        """
        Publica evento no stream apropriado.

        Returns:
            ID do evento no stream ou None em caso de erro
        """
        stream = self._stream_for_event(event)
        data = {
            "event": event,
            "instance_id": instance_id,
            "payload": json.dumps(payload) if isinstance(payload, dict) else str(payload),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": source,
        }
        if jid:
            data["jid"] = jid

        try:
            msg_id = self.client.xadd(stream, data, maxlen=10000)
            logger.info(f"[EventBus] Published {event} to {stream} id={msg_id}")
            return msg_id
        except redis.RedisError as e:
            logger.error(f"[EventBus] Failed to publish {event}: {e}")
            return None

    def publish_whatsapp(
        self,
        event_type: str,
        instance_id: str,
        payload: Dict[str, Any],
        jid: Optional[str] = None,
    ) -> Optional[str]:
        """Publica evento WhatsApp no stream whatsapp.inbound"""
        event = f"whatsapp.{event_type}"
        return self.publish(
            event=event,
            payload=payload,
            instance_id=instance_id,
            jid=jid,
            source="whatsapp_gateway_service",
        )

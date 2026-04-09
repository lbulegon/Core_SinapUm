"""
Event Bus Consumer - Consome eventos de Redis Streams
"""
import json
import logging
import os
import signal
import sys
from typing import Callable, Dict, Optional

import redis

logger = logging.getLogger(__name__)

STREAM_WHATSAPP_INBOUND = "whatsapp.inbound"
CONSUMER_GROUP = "event_consumers"
BLOCK_MS = 5000


class EventBusConsumer:
    """Consumidor de eventos de Redis Streams"""

    def __init__(
        self,
        redis_url: str,
        stream: str,
        consumer_name: str,
        handler: Callable[[Dict], None],
    ):
        self.redis_url = redis_url
        self.stream = stream
        self.consumer_name = consumer_name
        self.handler = handler
        self._client: Optional[redis.Redis] = None
        self._running = True

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    def _ensure_group(self):
        """Cria consumer group se não existir"""
        try:
            self.client.xgroup_create(
                self.stream, CONSUMER_GROUP, id="0", mkstream=True
            )
            logger.info(f"Created consumer group {CONSUMER_GROUP} for {self.stream}")
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                logger.warning(f"Consumer group creation: {e}")

    def _parse_message(self, data: Dict) -> Dict:
        """Parse payload JSON se necessário"""
        payload = data.get("payload", "{}")
        if isinstance(payload, str):
            try:
                data = {**data, "payload": json.loads(payload)}
            except json.JSONDecodeError:
                pass
        return data

    def run(self):
        """Loop principal de consumo"""
        self._ensure_group()
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        logger.info(f"Consumer {self.consumer_name} started for {self.stream}")

        while self._running:
            try:
                messages = self.client.xreadgroup(
                    CONSUMER_GROUP,
                    self.consumer_name,
                    {self.stream: ">"},
                    count=10,
                    block=BLOCK_MS,
                )
                for stream_name, stream_messages in messages:
                    for msg_id, data in stream_messages:
                        try:
                            parsed = self._parse_message(data)
                            self.handler(parsed)
                            self.client.xack(self.stream, CONSUMER_GROUP, msg_id)
                        except Exception as e:
                            logger.error(f"Handler error for {msg_id}: {e}")
                            # Não faz XACK - mensagem volta para pending
            except redis.ConnectionError as e:
                logger.error(f"Redis connection error: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Consumer error: {e}")

    def _shutdown(self, signum, frame):
        self._running = False
        logger.info("Consumer shutting down...")

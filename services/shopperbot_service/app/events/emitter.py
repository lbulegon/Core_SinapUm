"""Event emitter para analytics e tracking"""
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from enum import Enum
from app.utils.logging import logger
from app.utils.config import STORAGE_PATH


class EventType(str, Enum):
    """Tipos de eventos"""
    INTENT_DETECTED = "INTENT_DETECTED"
    PRODUCT_RECOMMENDED = "PRODUCT_RECOMMENDED"
    OBJECTION_HANDLED = "OBJECTION_HANDLED"
    CARD_GENERATED = "CARD_GENERATED"
    PRIVATE_CHAT_STARTED = "PRIVATE_CHAT_STARTED"
    HUMAN_HANDOFF = "HUMAN_HANDOFF"


class EventEmitter:
    """Emite eventos para analytics"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or STORAGE_PATH
        self.events_log = self.storage_path / "events.log"
    
    def emit(
        self,
        event_type: EventType,
        request_id: str,
        user_id: Optional[str] = None,
        group_id: Optional[str] = None,
        estabelecimento_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None
    ):
        """Emite um evento"""
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type.value,
            "ts": datetime.utcnow().isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "group_id": group_id,
            "estabelecimento_id": estabelecimento_id,
            "payload": payload or {}
        }
        
        # Log estruturado
        logger.info(
            f"Event: {event_type.value}",
            extra={
                "event": event,
                "request_id": request_id,
                "user_id": user_id,
                "estabelecimento_id": estabelecimento_id
            }
        )
        
        # Salvar em arquivo JSON (append)
        try:
            with open(self.events_log, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.warning(f"Erro ao salvar evento: {e}")


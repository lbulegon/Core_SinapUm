"""Logging estruturado para ShopBot Service"""
import logging
import json
import uuid
from datetime import datetime
from typing import Optional

logger = logging.getLogger("shopbot")
logger.setLevel(logging.INFO)

# Handler para JSON logs
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

class JSONFormatter(logging.Formatter):
    """Formatter que gera logs em JSON"""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Adicionar request_id se disponível
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # Adicionar campos extras
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "estabelecimento_id"):
            log_data["estabelecimento_id"] = record.estabelecimento_id
        
        # Adicionar exception se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

def get_request_id() -> str:
    """Gera um novo request_id"""
    return str(uuid.uuid4())


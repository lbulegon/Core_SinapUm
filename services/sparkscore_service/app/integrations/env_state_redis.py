"""
Espelho do EnvironmentalStateService Django — mesmas chaves Redis.

Usado pelo SparkScore quando REDIS_URL está definido (ex.: docker: ddf_redis:6379/2).
Desativar: ENVIRONMENTAL_STATE_REDIS_ENABLED=false
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def _client():
    if os.environ.get("ENVIRONMENTAL_STATE_REDIS_ENABLED", "true").lower() not in (
        "1",
        "true",
        "yes",
    ):
        return None
    try:
        import redis

        url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
        return redis.from_url(url, decode_responses=True)
    except Exception as exc:
        logger.debug("env_state_redis: Redis indisponível: %s", exc)
        return None


def _key(eid: str | int) -> str:
    return f"env_state:{eid}"


def _history_key(eid: str | int) -> str:
    return f"env_history:{eid}"


def push_environmental_state(estabelecimento_id: str | int, result: Dict[str, Any]) -> bool:
    """
    Grava env_state + env_history (mesmo contrato que services.environmental_state_service).
    `result`: saída de EnvironmentalIndiciaryOrbital.run()
    """
    r = _client()
    if r is None:
        return False
    ttl = int(os.environ.get("REDIS_TTL_ENV_STATE", "300"))
    history_max = int(os.environ.get("ENV_HISTORY_MAX_LEN", "100"))

    payload = {
        "score": result["score"],
        "state": result["state"],
        "confidence": result.get("confidence", 0.0),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "indicios": result.get("indicios", {}),
    }
    try:
        raw = json.dumps(payload, ensure_ascii=False)
        r.set(_key(estabelecimento_id), raw, ex=ttl)
        r.lpush(_history_key(estabelecimento_id), raw)
        r.ltrim(_history_key(estabelecimento_id), 0, history_max - 1)
        return True
    except Exception as exc:
        logger.warning("push_environmental_state falhou: %s", exc)
        return False

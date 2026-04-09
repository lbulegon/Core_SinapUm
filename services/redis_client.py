"""
Cliente Redis centralizado para o Core Django.

Usa REDIS_URL (preferencial) ou REDIS_HOST / REDIS_PORT / REDIS_DB.
Import de `redis` é lazy para não quebrar `migrate` / checks se o pacote não estiver instalado.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from django.conf import settings


def get_redis_client() -> Optional[Any]:
    """
    Retorna cliente Redis ou None se estado ambiental estiver desativado,
    pacote `redis` ausente ou conexão indisponível (fail-soft).
    """
    try:
        import redis
    except ImportError:
        return None

    if not getattr(settings, "ENVIRONMENTAL_STATE_REDIS_ENABLED", True):
        return None

    url = getattr(settings, "REDIS_URL", None) or os.environ.get("REDIS_URL")
    try:
        if url:
            return redis.from_url(url, decode_responses=True)
        host = getattr(settings, "REDIS_HOST", "localhost")
        port = int(getattr(settings, "REDIS_PORT", 6379))
        db = int(getattr(settings, "REDIS_DB", 0))
        return redis.Redis(host=host, port=port, db=db, decode_responses=True)
    except Exception:
        return None

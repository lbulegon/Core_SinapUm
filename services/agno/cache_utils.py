from __future__ import annotations

import hashlib
import json
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def _stable_json(obj: Any) -> str:
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)
    except Exception:
        return str(obj)


def make_cache_key(namespace: str, parts: list[Any]) -> str:
    digest = hashlib.sha256(_stable_json(parts).encode("utf-8")).hexdigest()[:24]
    return f"agno:{namespace}:{digest}"


def cache_get_or_set(key: str, ttl_seconds: int, factory: Callable[[], T]) -> T:
    """
    Cache best-effort: Django cache -> in-process TTL -> factory.
    """
    ttl_seconds = max(0, int(ttl_seconds or 0))

    try:
        from django.core.cache import cache

        cached = cache.get(key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        value = factory()
        if ttl_seconds > 0:
            cache.set(key, value, timeout=ttl_seconds)
        return value
    except Exception as exc:
        logger.debug("Agno cache indisponível (%s); executando sem cache", exc)

    # Fallback in-process (por processo worker)
    if not hasattr(cache_get_or_set, "_mem"):
        setattr(cache_get_or_set, "_mem", {})  # type: ignore[attr-defined]

    mem: dict[str, tuple[float, Any]] = getattr(cache_get_or_set, "_mem")  # type: ignore[attr-defined]
    now = time.time()
    hit = mem.get(key)
    if hit and (now - hit[0]) <= ttl_seconds:
        return hit[1]  # type: ignore[return-value]

    value = factory()
    mem[key] = (now, value)
    return value

import os
import time
from contextlib import contextmanager
from typing import Iterator, Optional

import redis


def _redis_client() -> redis.Redis:
    url = os.getenv("IDEMPOTENCY_REDIS_URL") or os.getenv("CELERY_BROKER_URL") or "redis://localhost:6379/0"
    return redis.Redis.from_url(url, decode_responses=True)


@contextmanager
def redis_lock(
    key: str,
    ttl_seconds: int = 120,
    wait_seconds: int = 0,
    poll_interval: float = 0.2,
) -> Iterator[bool]:
    """
    Lock simples por SET NX.
    - Se wait_seconds=0: tenta 1 vez e retorna acquired False/True.
    - Se wait_seconds>0: tenta até adquirir ou estourar tempo.
    """
    r = _redis_client()
    lock_value = str(int(time.time() * 1000))

    deadline: Optional[float] = None
    if wait_seconds > 0:
        deadline = time.time() + wait_seconds

    acquired = False
    try:
        while True:
            acquired = bool(r.set(key, lock_value, nx=True, ex=ttl_seconds))
            if acquired:
                break
            if deadline is None or time.time() > deadline:
                break
            time.sleep(poll_interval)

        yield acquired
    finally:
        # Libera apenas se este processo detém o lock
        if acquired:
            current = r.get(key)
            if current == lock_value:
                r.delete(key)


def idempotency_key(event_id: str) -> str:
    return f"core_sinapum:idempotency:{event_id}"

"""
Observabilidade da pipeline de autonomia (sem LLM como motor de decisão).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("cognitive.autonomy")


def log_autonomy(
    event: str,
    *,
    trace_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    extra = dict(payload or {})
    if trace_id:
        extra["trace_id"] = trace_id
    if tenant_id:
        extra["tenant_id"] = tenant_id
    logger.info("autonomy:%s %s", event, extra)

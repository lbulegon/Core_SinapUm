"""
Observabilidade cognitiva: trilha Perception → Reality → Decision → Outcome (trace_id único).
"""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger("cognitive.pipeline")


def log_pipeline_event(
    trace_id: str,
    stage: str,
    *,
    elapsed_ms: Optional[float] = None,
    payload: Optional[Dict[str, Any]] = None,
) -> None:
    extra = dict(payload or {})
    if elapsed_ms is not None:
        extra["elapsed_ms"] = round(elapsed_ms, 2)
    logger.info(
        "cognitive_pipeline trace_id=%s stage=%s %s",
        trace_id,
        stage,
        extra,
    )


class PipelineTimer:
    def __init__(self, trace_id: str, stage: str):
        self.trace_id = trace_id
        self.stage = stage
        self._t0 = time.perf_counter()

    def stop(self, **payload: Any) -> float:
        ms = (time.perf_counter() - self._t0) * 1000
        log_pipeline_event(self.trace_id, self.stage, elapsed_ms=ms, payload=payload)
        return ms

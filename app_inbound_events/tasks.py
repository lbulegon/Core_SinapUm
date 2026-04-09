"""
Tarefas Celery — ciclo de autonomia cognitiva (Fase 3).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, ignore_result=False)
def run_cognitive_autonomy_cycle(
    self,
    tenant_id: str,
    operational_snapshot: Optional[Dict[str, Any]] = None,
    dynamic_metrics: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Job periódico ou disparado por evento. Nível controlado por COGNITIVE_AUTONOMY_LEVEL.
    """
    from core.services.cognitive_core.autonomy.autonomous_loop import run_autonomous_cycle

    ol: Dict[str, Any] = {}
    if operational_snapshot:
        ol["client_operational_snapshot"] = operational_snapshot
        ol["operational_snapshot"] = operational_snapshot

    try:
        return run_autonomous_cycle(
            tenant_id=tenant_id,
            operational_live=ol,
            dynamic_metrics=dynamic_metrics,
        )
    except Exception as e:
        logger.exception("run_cognitive_autonomy_cycle failed: %s", e)
        return {"ok": False, "error": str(e)}

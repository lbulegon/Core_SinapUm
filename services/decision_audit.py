"""Auditoria de decisões do motor cognitivo (Django ORM)."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def snapshot_context_for_audit(context: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "estabelecimento_id",
        "trace_id",
        "environmental_mode",
        "objective",
    )
    out: dict[str, Any] = {}
    for k in keys:
        if k in context and context[k] is not None:
            try:
                out[k] = context[k]
            except Exception:
                out[k] = str(context[k])[:500]
    return out


def log_decision_response(
    *,
    module_name: str,
    decision: str,
    response: dict[str, Any] | None,
    context: dict[str, Any],
) -> None:
    try:
        from django.apps import apps

        if not apps.ready:
            return
        from app_sinapcore.models.sinapcore_log import SinapCoreLog

        action_type = response.get("type") if isinstance(response, dict) else None
        SinapCoreLog.objects.create(
            module=module_name,
            decision=decision,
            action=action_type,
            context=snapshot_context_for_audit(context),
        )
    except Exception:
        logger.debug("decision_audit: log ignorado", exc_info=True)

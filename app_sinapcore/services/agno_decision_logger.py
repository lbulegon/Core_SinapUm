from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ChefAgnoDecisionLogger:
    """
    Persistencia best-effort de decisoes do Chef Agno (auditoria/explicabilidade).
    """

    @staticmethod
    def log_decision(
        *,
        module: str,
        action: str,
        reason: str,
        product_id: int | None = None,
        product_name: str = "",
        payload: dict[str, Any] | None = None,
    ) -> int | None:
        try:
            from app_sinapcore.models.agno_decision_log import AgnoDecisionLog

            row = AgnoDecisionLog.objects.create(
                module=module[:40],
                action=action[:80],
                product_id=product_id,
                product_name=(product_name or "")[:120],
                reason=reason[:255],
                payload=payload or {},
            )
            return int(row.id)
        except Exception as exc:
            logger.warning("Falha ao persistir log Agno (%s): %s", action, exc)
            return None

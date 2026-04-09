from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class Observer:
    """
    OBSERVE: normaliza resultados brutos do orbital em observações auditáveis.

    Sem lógica de negócio — apenas estruturação e metadados de coleta.
    """

    def observe(
        self,
        *,
        step: dict[str, Any],
        raw_result: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "step_id": step.get("id"),
            "operation": step.get("operation"),
            "result": raw_result,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "success": bool(raw_result.get("ok", True)),
        }

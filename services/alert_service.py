"""
Alertas derivados de padrões em logs e (futuro) métricas — EOC / SinapCore.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class AlertService:
    """Regras leves sobre `SinapCoreLog` e extensível para Redis / PPA."""

    @staticmethod
    def check_environmental_alerts() -> dict[str, Any] | None:
        """
        Ex.: 3+ decisões ENV_CRITICAL nos últimos 5 logs ambientais → alerta recorrente.
        """
        try:
            from django.apps import apps

            if not apps.ready:
                return None
            from app_sinapcore.models.sinapcore_log import SinapCoreLog

            recent_logs = list(
                SinapCoreLog.objects.filter(module="environmental").order_by("-timestamp")[:5]
            )
            critical_count = sum(1 for log in recent_logs if log.decision == "ENV_CRITICAL")
            if critical_count >= 3:
                return {
                    "level": "critical",
                    "message": "Sobrecarga recorrente detectada (padrão ENV_CRITICAL nos logs recentes)",
                }
        except Exception:
            logger.debug("AlertService.check_environmental_alerts indisponível", exc_info=True)
        return None

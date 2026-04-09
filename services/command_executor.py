"""
Command Layer — enfileiramento automático + execução via `CommandExecutionRuntime`.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Fachada para fila EOC + runtime de handlers."""

    @staticmethod
    def _log_eoc(decision: str, action: str | None, extra: dict[str, Any] | None = None) -> None:
        try:
            from django.apps import apps

            if not apps.ready:
                return
            from app_sinapcore.models.sinapcore_log import SinapCoreLog

            ctx = {"layer": "command", **(extra or {})}
            SinapCoreLog.objects.create(
                module="EOC",
                decision=decision,
                action=action,
                context=ctx,
            )
        except Exception:
            logger.debug("CommandExecutor: audit log falhou", exc_info=True)

    @staticmethod
    def enqueue_automatic_commands(context: dict[str, Any]) -> None:
        try:
            from django.apps import apps

            if not apps.ready:
                return
            from app_sinapcore.models.sinapcore_command import SinapCoreCommand
            from services.environmental_state_service import EnvironmentalStateService
            from services.system_mode_service import compute_mode_from_env_dict
        except Exception:
            return

        eid = context.get("estabelecimento_id")
        if eid is None:
            return

        raw = EnvironmentalStateService.get_state(eid)
        if not raw:
            return

        state = (raw.get("state") or "").strip().lower()
        mode = compute_mode_from_env_dict(raw)

        def _pending(kind: str) -> bool:
            return SinapCoreCommand.objects.filter(
                executed=False, command=kind, source="auto"
            ).exists()

        if mode == "CRITICAL" and state == "colapso" and not _pending("pause_orders"):
            SinapCoreCommand.objects.create(
                command="pause_orders",
                status="pending",
                source="auto",
                payload={"reason": "ambient_colapso", "estabelecimento_id": eid},
            )
            CommandExecutor._log_eoc(
                "auto_enqueue",
                "pause_orders",
                {"estabelecimento_id": eid, "env_state": state},
            )
        elif mode == "PRESSURE" and state == "sobrecarga" and not _pending("reduce_load"):
            SinapCoreCommand.objects.create(
                command="reduce_load",
                status="pending",
                source="auto",
                payload={"reason": "ambient_sobrecarga", "estabelecimento_id": eid},
            )
            CommandExecutor._log_eoc(
                "auto_enqueue",
                "reduce_load",
                {"estabelecimento_id": eid, "env_state": state},
            )

    @staticmethod
    def execute_pending(context: dict[str, Any] | None = None) -> int:
        from services.command_execution_runtime import CommandExecutionRuntime

        return CommandExecutionRuntime.execute_pending(context)

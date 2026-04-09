"""
Execução de comandos com ORM Django + handlers do `command_engine` (sem lógica if/elif).
"""

from __future__ import annotations

import logging
from typing import Any

from command_engine.registry import CommandRegistry

logger = logging.getLogger(__name__)


class CommandExecutionRuntime:
    """Processa fila `SinapCoreCommand` com transação e auditoria."""

    @staticmethod
    def execute_pending(context: dict[str, Any] | None = None) -> int:
        try:
            from django.apps import apps
            from django.db import transaction

            if not apps.ready:
                return 0
            from app_sinapcore.models.sinapcore_command import SinapCoreCommand
            from app_sinapcore.models.sinapcore_log import SinapCoreLog
        except Exception:
            logger.debug("command_execution_runtime: Django indisponível", exc_info=True)
            return 0

        ctx = context or {}
        processed = 0

        with transaction.atomic():
            cmds = list(
                SinapCoreCommand.objects.filter(executed=False)
                .order_by("created_at")
                .select_for_update()
            )

            for cmd in cmds:
                handler = CommandRegistry.get(cmd.command)
                if not handler:
                    logger.warning("Sem handler para comando=%s (id=%s)", cmd.command, cmd.id)
                    cmd.status = "failed"
                    cmd.executed = True
                    cmd.save(update_fields=["status", "executed"])
                    try:
                        SinapCoreLog.objects.create(
                            module="command_engine",
                            decision=cmd.command,
                            action="no_handler",
                            context={"command_id": cmd.id, "payload": cmd.payload},
                        )
                    except Exception:
                        logger.debug("log falhou", exc_info=True)
                    continue

                try:
                    cmd.status = "running"
                    cmd.save(update_fields=["status"])

                    if not handler.can_execute(cmd):
                        cmd.status = "failed"
                        cmd.executed = True
                        cmd.save(update_fields=["status", "executed"])
                        SinapCoreLog.objects.create(
                            module="command_engine",
                            decision=cmd.command,
                            action="blocked",
                            context={"reason": "can_execute_false", "command_id": cmd.id},
                        )
                        continue

                    result = handler.execute(cmd, ctx)
                    handler.on_success(cmd, result)

                    cmd.status = "done"
                    cmd.executed = True
                    cmd.save(update_fields=["status", "executed"])

                    SinapCoreLog.objects.create(
                        module="command_engine",
                        decision=cmd.command,
                        action="executed",
                        context={"result": result, "payload": cmd.payload},
                    )
                    processed += 1

                except Exception as exc:
                    err = str(exc)
                    logger.exception("Falha no comando id=%s", cmd.id)
                    try:
                        handler.on_failure(cmd, err)
                    except Exception:
                        logger.exception("on_failure falhou")

                    cmd.status = "failed"
                    cmd.executed = True
                    cmd.save(update_fields=["status", "executed"])

                    try:
                        SinapCoreLog.objects.create(
                            module="command_engine",
                            decision=cmd.command,
                            action="failed",
                            context={"error": err, "command_id": cmd.id},
                        )
                    except Exception:
                        logger.debug("log de falha falhou", exc_info=True)

        return processed

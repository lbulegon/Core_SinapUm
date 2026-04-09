from __future__ import annotations

import logging
from typing import Any

from agent_core.registry.module_registry import ModuleDescriptor, ModuleRegistry
from services.alert_service import AlertService
from services.command_executor import CommandExecutor
from services.decision_audit import log_decision_response

logger = logging.getLogger(__name__)


class SinapEngine:
    """
    Motor PAOR: percebe → analisa → orquestra → responde.
    Infra (fila de comandos, logs ORM) via `services`.
    """

    def __init__(self) -> None:
        pass

    def run(self, context: dict[str, Any]) -> dict[str, Any]:
        try:
            CommandExecutor.enqueue_automatic_commands(context)
            CommandExecutor.execute_pending(context)
        except Exception:
            logger.exception("SinapEngine: CommandExecutor falhou")

        modules: list[ModuleDescriptor] = ModuleRegistry.get_active_modules()
        perceptions: list[dict[str, Any]] = []
        analyses: list[dict[str, Any]] = []
        decisions: list[str] = []
        actions: list[dict[str, Any]] = []

        for m in modules:
            try:
                p = m.perceptor.perceive(context)
                if p:
                    perceptions.append(p)
            except Exception:
                logger.exception("SinapEngine: perceptor falhou (módulo=%s)", m.name)

        for m in modules:
            for p in perceptions:
                if p.get("module") == m.name:
                    try:
                        a = m.analyzer.analyze(p)
                        analyses.append(a)
                    except Exception:
                        logger.exception("SinapEngine: analyzer falhou (módulo=%s)", m.name)

        for m in modules:
            try:
                d = m.orchestrator.decide(analyses)
                if d:
                    decisions.append(d)
            except Exception:
                logger.exception("SinapEngine: orchestrator falhou (módulo=%s)", m.name)

        actions = self._collect_actions(modules, decisions, context)

        pattern = AlertService.check_environmental_alerts()
        if pattern:
            actions.append(
                {
                    "type": "alert",
                    "source": "eoc_pattern",
                    "level": pattern.get("level"),
                    "message": pattern["message"],
                    "module": "environmental",
                }
            )

        return {
            "perceptions": perceptions,
            "analyses": analyses,
            "decisions": decisions,
            "actions": actions,
        }

    def _collect_actions(
        self,
        modules: list[ModuleDescriptor],
        decisions: list[str],
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in modules:
            for d in decisions:
                try:
                    r = m.responder.handle(d, context)
                    log_decision_response(
                        module_name=m.name,
                        decision=d,
                        response=r,
                        context=context,
                    )
                    if r:
                        out.append(r)
                except Exception:
                    logger.exception("SinapEngine: responder falhou (módulo=%s)", m.name)
        return out

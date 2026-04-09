from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from django.db import transaction

from agent_core.models.agent_run import AgentRun


class StateManager:
    """
    Persistência transacional do AgentRun e append imutável ao histórico de auditoria.

    Cada etapa PAOR grava um bloco com input, output, timestamp e decisão.
    """

    def create_run(self, objective: str, initial_state: dict[str, Any] | None = None) -> AgentRun:
        return AgentRun.objects.create(
            objetivo=objective,
            estado_atual=initial_state or {},
            historico=[],
            iteracao=0,
            status=AgentRun.Status.RUNNING,
        )

    @transaction.atomic
    def append_audit(
        self,
        run: AgentRun,
        *,
        phase: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        decision: str,
    ) -> None:
        entry = {
            "phase": phase,
            "input": input_data,
            "output": output_data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "decision": decision,
        }
        hist = list(run.historico or [])
        hist.append(entry)
        run.historico = hist
        run.save(update_fields=["historico", "updated_at"])

    @transaction.atomic
    def update_iteration(self, run: AgentRun, iteration: int, estado: dict[str, Any]) -> None:
        """Mescla `estado` em `estado_atual` para não apagar `architecture_evaluation` / governança inicial."""
        prev = dict(run.estado_atual or {})
        prev.update(estado)
        run.iteracao = iteration
        run.estado_atual = prev
        run.save(update_fields=["iteracao", "estado_atual", "updated_at"])

    @transaction.atomic
    def set_plan(self, run: AgentRun, plan: dict[str, Any]) -> None:
        run.plano = plan
        run.save(update_fields=["plano", "updated_at"])

    @transaction.atomic
    def set_status(
        self,
        run: AgentRun,
        status: str,
        *,
        error_message: str = "",
    ) -> None:
        run.status = status
        run.error_message = error_message
        run.save(update_fields=["status", "error_message", "updated_at"])

    def refresh(self, run: AgentRun) -> AgentRun:
        run.refresh_from_db()
        return run

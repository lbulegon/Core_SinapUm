"""
DjangoRepository - usa modelos Django para persistência.

Requer Django configurado (DJANGO_SETTINGS_MODULE, django.setup()).
Converte entre modelos Django e dataclasses do serviço.
"""
from datetime import datetime
from typing import List, Optional

from .models import (
    ArchitectureCycle as CycleModel,
    ArchitectureStageRun as StageRunModel,
    ArchitectureDecisionLog as DecisionModel,
    ArchitectureRisk as RiskModel,
)

# Import domain models from the service
import sys
from pathlib import Path
_svc = Path(__file__).resolve().parent.parent / "services" / "architecture_intelligence_service"
if str(_svc) not in sys.path:
    sys.path.insert(0, str(_svc))
from app.models import (
    ArchitectureArtifact,
    ArchitectureCycle,
    ArchitectureStageRun,
    ArchitectureDecisionLog,
    ArchitectureRisk,
)


def _artifact_from_cycle(m: CycleModel) -> ArchitectureArtifact:
    return ArchitectureArtifact(
        content=m.artifact_content,
        artifact_type=m.artifact_type or "document",
        domain_id=m.artifact_domain_id,
        metadata=m.artifact_metadata or {},
        created_at=m.created_at,
    )


def _cycle_to_domain(m: CycleModel) -> ArchitectureCycle:
    return ArchitectureCycle(
        id=m.id,
        cycle_type=m.cycle_type,
        state=m.state,
        artifact=_artifact_from_cycle(m),
        trace_id=m.trace_id,
        started_at=m.started_at,
        completed_at=m.completed_at,
        metadata=m.metadata or {},
    )


def _run_to_domain(m: StageRunModel) -> ArchitectureStageRun:
    return ArchitectureStageRun(
        id=m.id,
        cycle_id=m.cycle_id,
        stage=m.stage,
        state=m.state,
        input_content=m.input_content,
        output_content=m.output_content or "",
        started_at=m.started_at,
        completed_at=m.completed_at,
        error_message=m.error_message,
        metadata=m.metadata or {},
    )


class DjangoRepository:
    """Repositório que usa Django ORM."""

    def save_cycle(self, cycle: ArchitectureCycle) -> None:
        art = cycle.artifact
        CycleModel.objects.update_or_create(
            id=cycle.id,
            defaults={
                "cycle_type": cycle.cycle_type,
                "state": cycle.state,
                "artifact_content": art.content,
                "artifact_type": art.artifact_type,
                "artifact_domain_id": art.domain_id,
                "artifact_metadata": art.metadata,
                "trace_id": cycle.trace_id,
                "started_at": cycle.started_at,
                "completed_at": cycle.completed_at,
                "metadata": cycle.metadata,
            },
        )

    def get_cycle(self, cycle_id: str) -> Optional[ArchitectureCycle]:
        try:
            m = CycleModel.objects.get(id=cycle_id)
            return _cycle_to_domain(m)
        except CycleModel.DoesNotExist:
            return None

    def save_stage_run(self, run: ArchitectureStageRun) -> None:
        StageRunModel.objects.update_or_create(
            id=run.id,
            defaults={
                "cycle_id": run.cycle_id,
                "stage": run.stage,
                "state": run.state,
                "input_content": run.input_content,
                "output_content": run.output_content,
                "started_at": run.started_at,
                "completed_at": run.completed_at,
                "error_message": run.error_message,
                "metadata": run.metadata,
            },
        )

    def get_stage_runs(self, cycle_id: str) -> List[ArchitectureStageRun]:
        return [_run_to_domain(m) for m in StageRunModel.objects.filter(cycle_id=cycle_id).order_by("created_at")]

    def save_decision(self, decision: ArchitectureDecisionLog) -> None:
        DecisionModel.objects.update_or_create(
            id=decision.id,
            defaults={
                "cycle_id": decision.cycle_id,
                "stage": decision.stage,
                "decision": decision.decision,
                "rationale": decision.rationale,
            },
        )

    def get_decisions(self, cycle_id: str) -> List[ArchitectureDecisionLog]:
        return [
            ArchitectureDecisionLog(
                id=m.id,
                cycle_id=m.cycle_id,
                stage=m.stage,
                decision=m.decision,
                rationale=m.rationale,
                created_at=m.created_at,
            )
            for m in DecisionModel.objects.filter(cycle_id=cycle_id)
        ]

    def save_risk(self, risk: ArchitectureRisk) -> None:
        RiskModel.objects.update_or_create(
            id=risk.id,
            defaults={
                "cycle_id": risk.cycle_id,
                "stage": risk.stage,
                "risk_description": risk.risk_description,
                "severity": risk.severity,
                "mitigation": risk.mitigation,
            },
        )

    def get_risks(self, cycle_id: str) -> List[ArchitectureRisk]:
        return [
            ArchitectureRisk(
                id=m.id,
                cycle_id=m.cycle_id,
                stage=m.stage,
                risk_description=m.risk_description,
                severity=m.severity,
                mitigation=m.mitigation,
                created_at=m.created_at,
            )
            for m in RiskModel.objects.filter(cycle_id=cycle_id)
        ]

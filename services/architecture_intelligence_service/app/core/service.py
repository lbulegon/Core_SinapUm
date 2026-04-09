"""Service facade."""
from typing import List, Optional
from .enums import ArchitectureStage
from .exceptions import CycleNotFoundError
from .models import ArchitectureCycle, ArchitectureStageRun
from .orchestrator import ArchitectureOrchestrator
from .repository import InMemoryRepository
from .stages import StageExecutor
from app.adapters.llm_adapter import get_llm_adapter

class ArchitectureIntelligenceService:
    def __init__(self):
        self.llm = get_llm_adapter("openmind")
        self.repo = InMemoryRepository()
        self.executor = StageExecutor(self.llm)
        self.orchestrator = ArchitectureOrchestrator(self.executor, self.repo)

    def start_architecture_cycle(self, artifact_content: str, cycle_type: str = "full_cycle", trace_id: Optional[str] = None) -> ArchitectureCycle:
        return self.orchestrator.start_architecture_cycle(artifact_content, cycle_type, trace_id)

    def run_stage(self, cycle_id: str, stage: str, input_content: Optional[str] = None) -> ArchitectureStageRun:
        return self.orchestrator.run_stage(cycle_id, ArchitectureStage(stage), input_content)

    def get_cycle_report(self, cycle_id: str) -> dict:
        cycle = self.repo.get_cycle(cycle_id)
        if not cycle:
            raise CycleNotFoundError(cycle_id)
        runs = self.repo.get_stage_runs(cycle_id)
        return {
            "cycle_id": cycle.id,
            "cycle_type": cycle.cycle_type,
            "state": cycle.state,
            "trace_id": cycle.trace_id,
            "stage_runs": [{"stage": r.stage, "state": r.state, "output_preview": r.output_content[:500] + "..." if len(r.output_content) > 500 else r.output_content} for r in runs],
            "started_at": str(cycle.started_at),
            "completed_at": str(cycle.completed_at),
        }

    def list_stage_runs(self, cycle_id: str) -> List[ArchitectureStageRun]:
        return self.repo.get_stage_runs(cycle_id)

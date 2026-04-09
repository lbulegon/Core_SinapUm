"""Orchestrator."""
from datetime import datetime
import uuid
from typing import Optional
from .enums import ArchitectureStage, CycleState, CycleType, CYCLE_STAGES
from .exceptions import CycleNotFoundError, InvalidCycleTypeError
from .models import ArchitectureArtifact, ArchitectureCycle, ArchitectureStageRun
from .repository import InMemoryRepository
from .stages import StageExecutor

class ArchitectureOrchestrator:
    def __init__(self, executor: StageExecutor, repo: InMemoryRepository):
        self.executor = executor
        self.repo = repo

    def start_architecture_cycle(self, artifact_content: str, cycle_type: str = "full_cycle", trace_id: Optional[str] = None) -> ArchitectureCycle:
        try:
            CycleType(cycle_type)
        except ValueError:
            raise InvalidCycleTypeError(f"Invalid: {cycle_type}")
        cid = str(uuid.uuid4())
        art = ArchitectureArtifact(content=artifact_content, created_at=datetime.utcnow())
        cycle = ArchitectureCycle(id=cid, cycle_type=cycle_type, state=CycleState.CREATED.value, artifact=art, trace_id=trace_id, started_at=datetime.utcnow())
        self.repo.save_cycle(cycle)
        return cycle

    def run_stage(self, cycle_id: str, stage: ArchitectureStage, input_content: Optional[str] = None) -> ArchitectureStageRun:
        cycle = self.repo.get_cycle(cycle_id)
        if not cycle:
            raise CycleNotFoundError(cycle_id)
        content = input_content or cycle.artifact.content
        prev = {r.stage: r.output_content for r in self.repo.get_stage_runs(cycle_id) if r.stage != stage.value}
        run = self.executor.run(stage, content, str(uuid.uuid4()), cycle_id, prev if prev else None)
        self.repo.save_stage_run(run)
        return run

    def run_full_cycle(self, cycle_id: str) -> ArchitectureCycle:
        cycle = self.repo.get_cycle(cycle_id)
        if not cycle:
            raise CycleNotFoundError(cycle_id)
        cycle.state = CycleState.RUNNING.value
        self.repo.save_cycle(cycle)
        stages = CYCLE_STAGES.get(CycleType(cycle.cycle_type), [])
        content = cycle.artifact.content
        for s in stages:
            r = self.run_stage(cycle_id, s, content)
            content = r.output_content
        cycle.state = CycleState.COMPLETED.value
        cycle.completed_at = datetime.utcnow()
        self.repo.save_cycle(cycle)
        return cycle

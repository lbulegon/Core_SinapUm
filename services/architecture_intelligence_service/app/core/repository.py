"""In-memory repository."""
from typing import Dict, List, Optional
from .models import ArchitectureCycle, ArchitectureStageRun

class InMemoryRepository:
    def __init__(self):
        self._cycles: Dict[str, ArchitectureCycle] = {}
        self._runs: Dict[str, ArchitectureStageRun] = {}

    def save_cycle(self, c: ArchitectureCycle): self._cycles[c.id] = c
    def get_cycle(self, id: str) -> Optional[ArchitectureCycle]: return self._cycles.get(id)
    def save_stage_run(self, r: ArchitectureStageRun): self._runs[r.id] = r
    def get_stage_runs(self, cycle_id: str) -> List[ArchitectureStageRun]:
        return [r for r in self._runs.values() if r.cycle_id == cycle_id]

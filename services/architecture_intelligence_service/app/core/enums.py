"""Enums."""
from enum import Enum

class CycleState(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class CycleType(str, Enum):
    FULL_CYCLE = "full_cycle"
    DESIGN_CYCLE = "design_cycle"
    REVIEW_CYCLE = "review_cycle"
    GOVERNANCE_CYCLE = "governance_cycle"
    STRESS_CYCLE = "stress_cycle"
    EVOLUTION_CYCLE = "evolution_cycle"

class ArchitectureStage(str, Enum):
    DESIGN = "design"
    REVIEW = "review"
    REFINE = "refine"
    THINK = "think"
    EVOLVE = "evolve"
    GOVERN = "govern"
    STRESS = "stress"

STAGE_TO_ROLE = {
    ArchitectureStage.DESIGN: "chief_architect",
    ArchitectureStage.REVIEW: "architecture_review_board",
    ArchitectureStage.REFINE: "refinement_engine",
    ArchitectureStage.THINK: "chief_systems_thinker",
    ArchitectureStage.EVOLVE: "system_evolution_architect",
    ArchitectureStage.GOVERN: "platform_governance_architect",
    ArchitectureStage.STRESS: "system_stress_tester",
}

CYCLE_STAGES = {
    CycleType.FULL_CYCLE: list(ArchitectureStage),
    CycleType.DESIGN_CYCLE: [ArchitectureStage.DESIGN, ArchitectureStage.REVIEW, ArchitectureStage.REFINE],
    CycleType.REVIEW_CYCLE: [ArchitectureStage.REVIEW, ArchitectureStage.REFINE],
    CycleType.GOVERNANCE_CYCLE: [ArchitectureStage.GOVERN],
    CycleType.STRESS_CYCLE: [ArchitectureStage.STRESS],
    CycleType.EVOLUTION_CYCLE: [ArchitectureStage.THINK, ArchitectureStage.EVOLVE],
}

"""
Grafo de apps Django ``app_*``, acoplamento, ciclos (SCC) e serialização para UI.
"""

from app_sinaplint.engine.graph.architecture_report import (
    build_architecture_report,
    compute_architecture_score,
)
from app_sinaplint.engine.graph.architectural_insights import (
    build_insights_payload,
    compute_architectural_risk,
)
from app_sinaplint.engine.graph.refactor_plan import RefactorPlanGenerator
from app_sinaplint.engine.graph.refactor_priority import RefactorImpactAnalyzer
from app_sinaplint.engine.graph.coupling_analyzer import CouplingAnalyzer
from app_sinaplint.engine.graph.cycle_detector import CycleDetector
from app_sinaplint.engine.graph.django_graph import DjangoAppGraph
from app_sinaplint.engine.graph.graph_serializer import to_nodes_edges

__all__ = [
    "CouplingAnalyzer",
    "CycleDetector",
    "DjangoAppGraph",
    "build_architecture_report",
    "build_insights_payload",
    "compute_architecture_score",
    "compute_architectural_risk",
    "RefactorImpactAnalyzer",
    "RefactorPlanGenerator",
    "to_nodes_edges",
]

"""
Relatório arquitetural agregado (grafo, acoplamento, ciclos, visual) e score de penalização.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.graph.architectural_insights import build_insights_payload
from app_sinaplint.engine.graph.coupling_analyzer import CouplingAnalyzer
from app_sinaplint.engine.graph.cycle_detector import CycleDetector
from app_sinaplint.engine.graph.django_graph import DjangoAppGraph
from app_sinaplint.engine.graph.graph_serializer import to_nodes_edges


def build_architecture_report(root: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    dg = DjangoAppGraph(root)
    data = dg.build()
    graph = data["graph"]
    coupling = CouplingAnalyzer().analyze(graph)
    cycles = CycleDetector().detect(graph)
    visual = to_nodes_edges(graph)
    arch: dict[str, Any] = {
        "apps": data["apps"],
        "graph": graph,
        "coupling": coupling,
        "cycles": cycles,
        "visual": visual,
        "edges_weighted": data["edges"],
        "fan_in": data["fan_in"],
    }
    insights = build_insights_payload(arch)
    arch["visual"] = insights["visual"]
    arch["insights"] = {
        "anti_patterns": insights["anti_patterns"],
        "refactor_priority": insights["refactor_priority"],
        "risk": insights["risk"],
    }
    return arch


def compute_architecture_score(architecture: dict[str, Any]) -> int:
    """
    Penaliza ciclos (SCC) e apps com ≥5 dependências de saída para outros ``app_*``.
    """
    penalty = 0
    cycles = architecture.get("cycles") or []
    penalty += len(cycles) * 15
    coupling_score = (architecture.get("coupling") or {}).get("coupling_score") or {}
    for _, count in coupling_score.items():
        if int(count) >= 5:
            penalty += 5
    return max(0, 100 - penalty)

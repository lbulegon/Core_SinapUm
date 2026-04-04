"""
Análise de Clean Architecture (camadas) e plano de refactor sugerido.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.architecture.clean_arch_analyzer import CleanArchitectureAnalyzer
from app_sinaplint.engine.architecture.dependency_extractor import DependencyExtractor
from app_sinaplint.engine.architecture.layer_mapper import LayerMapper
from app_sinaplint.engine.architecture.refactor_planner import RefactorPlanner


def build_clean_architecture_report(root: Path | str) -> dict[str, Any]:
    root = Path(root).resolve()
    analyzer = CleanArchitectureAnalyzer()
    violations = analyzer.analyze(root)
    planner = RefactorPlanner()
    plan = planner.generate(violations)
    return {
        "violations": violations,
        "refactor_plan": plan,
        "summary": {
            "violations_count": len(violations),
            "plan_items": len(plan),
        },
    }


__all__ = [
    "CleanArchitectureAnalyzer",
    "DependencyExtractor",
    "LayerMapper",
    "RefactorPlanner",
    "build_clean_architecture_report",
]

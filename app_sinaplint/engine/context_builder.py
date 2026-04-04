"""
Constrói contexto estrutural da raiz do monólito: apps Django ``app_*`` e dependências.

Delega a construção do grafo a :mod:`app_sinaplint.engine.graph` (uma única passagem
quando o orquestrador partilha o relatório ``arch``).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from app_sinaplint.engine.graph.architecture_report import build_architecture_report


def _scores_from_graph(
    code_score: int,
    *,
    apps_count: int,
    edges: list[dict[str, Any]],
    fan_in: dict[str, int],
) -> dict[str, int]:
    total_weight = sum(int(e.get("weight", 0)) for e in edges)
    max_fan = max(fan_in.values()) if fan_in else 0

    if apps_count <= 1:
        arch = 100
        mod = 100
    else:
        arch = max(0, 100 - min(55, total_weight * 2 // max(1, apps_count)))
        mod = max(0, 100 - min(50, max_fan * 3))

    return {
        "code": int(code_score),
        "architecture": int(arch),
        "modularity": int(mod),
    }


class AnalysisContextBuilder:
    """Descobre apps ``app_*``, pasta ``services`` e dependências cruzadas (imports)."""

    def build(self, root: Path) -> dict[str, Any]:
        """Uma passagem completa (grafo AST). Preferir ``build_from_arch`` no orquestrador."""
        return self.build_from_arch(root, build_architecture_report(root))

    def build_from_arch(self, root: Path, arch: dict[str, Any]) -> dict[str, Any]:
        root = root.resolve()
        has_services = (root / "services").is_dir()
        edges = arch.get("edges_weighted") or []
        return {
            "root_path": str(root),
            "django_apps": list(arch.get("apps") or []),
            "services": ["services"] if has_services else [],
            "django_app_dependencies": dict(arch.get("graph") or {}),
            "django_app_dependency_edges": edges,
            "django_app_fan_in": dict(arch.get("fan_in") or {}),
            "metrics": {
                "django_apps_count": len(arch.get("apps") or []),
                "cross_app_dependency_edges": len(edges),
                "total_dependency_weight": sum(int(e.get("weight", 0)) for e in edges),
            },
        }

    def build_scores(self, context: dict[str, Any], code_score: int) -> dict[str, int]:
        apps_count = int(context.get("metrics", {}).get("django_apps_count", 0))
        edges = list(context.get("django_app_dependency_edges") or [])
        fan_in = dict(context.get("django_app_fan_in") or {})
        return _scores_from_graph(
            code_score,
            apps_count=apps_count,
            edges=edges,
            fan_in=fan_in,
        )

    def build_scores_from_arch(self, arch: dict[str, Any], code_score: int) -> dict[str, int]:
        apps_count = len(arch.get("apps") or [])
        edges = list(arch.get("edges_weighted") or [])
        fan_in = dict(arch.get("fan_in") or {})
        return _scores_from_graph(
            code_score,
            apps_count=apps_count,
            edges=edges,
            fan_in=fan_in,
        )

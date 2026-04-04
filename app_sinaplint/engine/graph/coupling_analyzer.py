"""
Métricas de acoplamento por app (número de dependências de saída para outros ``app_*``).
"""

from __future__ import annotations

from typing import Any


class CouplingAnalyzer:
    def analyze(self, graph: dict[str, list[str] | set[str] | frozenset]) -> dict[str, Any]:
        coupling_score: dict[str, int] = {}
        issues: list[str] = []

        all_apps = set(graph.keys()) | {
            t for vs in graph.values() for t in (vs if isinstance(vs, (list, set, frozenset)) else [])
        }
        for app in sorted(all_apps):
            deps = _as_set(graph.get(app, []))
            count = len(deps)
            coupling_score[app] = count
            if count >= 5:
                issues.append(f"{app} altamente acoplado ({count} dependências)")

        return {
            "coupling_score": coupling_score,
            "issues": issues,
        }


def _as_set(vs: list[str] | set[str] | frozenset) -> set[str]:
    if isinstance(vs, set):
        return vs
    return set(vs) if vs else set()

"""
Impacto de refactor por app (investidor): combina fan-in, saídas, ciclos e acoplamento alto.
"""

from __future__ import annotations

from typing import Any


class RefactorImpactAnalyzer:
    """
    ``impact_score = fan_in*3 + out_degree*2 + cycle_participation*20 + high_coupling*10``

    ``out_degree`` = número de apps destino distintos no grafo (``len(graph[app])``).
    ``high_coupling`` = ``coupling_score[app] >= 5`` (mesmo critério já usado no score global).
    """

    def compute(self, arch: dict[str, Any]) -> list[dict[str, Any]]:
        graph: dict[str, list[str]] = dict(arch.get("graph") or {})
        fan_in: dict[str, int] = {k: int(v) for k, v in (arch.get("fan_in") or {}).items()}
        coupling = dict((arch.get("coupling") or {}).get("coupling_score") or {})
        cycles: list[list[str]] = list(arch.get("cycles") or [])

        cycle_map: dict[str, int] = {}
        for cycle in cycles:
            for app in cycle:
                cycle_map[app] = cycle_map.get(app, 0) + 1

        all_apps: set[str] = set(graph.keys())
        for vs in graph.values():
            for t in vs or []:
                all_apps.add(t)

        priorities: list[dict[str, Any]] = []
        for app in sorted(all_apps):
            deps = graph.get(app) or []
            if isinstance(deps, set):
                deps = list(deps)
            out_n = len(deps)
            fi = int(fan_in.get(app, 0))
            cpart = int(cycle_map.get(app, 0))
            coup_n = int(coupling.get(app, 0))
            high_c = coup_n >= 5

            impact = fi * 3 + out_n * 2 + cpart * 20 + (10 if high_c else 0)

            priorities.append(
                {
                    "app": app,
                    "impact_score": int(impact),
                    "fan_in": fi,
                    "dependencies": out_n,
                    "in_cycles": cpart,
                    "high_coupling": high_c,
                }
            )

        return sorted(priorities, key=lambda x: (-x["impact_score"], x["app"]))

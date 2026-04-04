"""
Deteção de dependências circulares entre apps via componentes fortemente conexas (Tarjan).

Cada ciclo arquitetural é reportado como a lista de nós num SCC com |SCC| ≥ 2
(mutual reachability = potencial ciclo de imports).
"""

from __future__ import annotations


class CycleDetector:
    def detect(self, graph: dict[str, list[str] | set[str]]) -> list[list[str]]:
        """Lista de SCCs com pelo menos 2 apps (ciclos / dependência mútua)."""
        return _tarjan_scc_cycles(graph)


def _tarjan_scc_cycles(graph: dict[str, list[str] | set[str]]) -> list[list[str]]:
    all_nodes: set[str] = set(graph.keys())
    for vs in graph.values():
        all_nodes |= set(vs)

    g: dict[str, list[str]] = {n: list(graph.get(n, []) or []) for n in all_nodes}

    index = 0
    stack: list[str] = []
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    sccs: list[list[str]] = []

    def strongconnect(v: str) -> None:
        nonlocal index
        indices[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        on_stack.add(v)

        for w in g.get(v, []):
            if w not in indices:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in on_stack:
                lowlink[v] = min(lowlink[v], indices[w])

        if lowlink[v] == indices[v]:
            comp: list[str] = []
            while True:
                w = stack.pop()
                on_stack.discard(w)
                comp.append(w)
                if w == v:
                    break
            if len(comp) >= 2:
                sccs.append(sorted(comp))

    for v in sorted(all_nodes):
        if v not in indices:
            strongconnect(v)

    return sorted(sccs, key=lambda x: (len(x), x))

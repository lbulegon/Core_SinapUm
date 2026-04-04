"""
Formato ``nodes`` / ``edges`` para bibliotecas de grafo (D3, Cytoscape, etc.).
"""

from __future__ import annotations


def to_nodes_edges(graph: dict[str, list[str] | set[str]]) -> dict[str, list[dict[str, str]]]:
    nodes = [{"id": app} for app in sorted(graph.keys())]
    # Incluir nós que só aparecem como destino
    targets = {t for vs in graph.values() for t in (vs if isinstance(vs, (list, set)) else [])}
    for t in sorted(targets):
        if t not in graph:
            nodes.append({"id": t})
    nodes = sorted(nodes, key=lambda x: x["id"])

    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for source, targets in graph.items():
        ts = targets if isinstance(targets, (list, set)) else []
        for target in sorted(ts):
            key = (source, target)
            if key in seen:
                continue
            seen.add(key)
            edges.append({"source": source, "target": target})

    return {"nodes": nodes, "edges": edges}

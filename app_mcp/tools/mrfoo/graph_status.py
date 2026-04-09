"""Tool mrfoo.graph.status — status do grafo FKG + health Neo4j."""
from typing import Any, Dict

from adapters.mrfoo_adapter import graph_status as adapter_graph_status


def graph_status(tenant_id: str) -> Dict[str, Any]:
    """Retorna status do grafo e conexão Neo4j para o tenant."""
    return adapter_graph_status(tenant_id)

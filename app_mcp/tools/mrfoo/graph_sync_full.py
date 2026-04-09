"""Tool mrfoo.graph.sync_full — sync completo Postgres to Neo4j."""
from typing import Any, Dict

from adapters.mrfoo_adapter import graph_sync_full as adapter_sync_full


def graph_sync_full(tenant_id: str) -> Dict[str, Any]:
    """Dispara sync completo do tenant para o WorldGraph."""
    return adapter_sync_full(tenant_id)

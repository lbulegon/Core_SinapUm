"""Tool mrfoo.graph.sync_incremental — sync incremental."""
from typing import Any, Dict

from adapters.mrfoo_adapter import graph_sync_incremental as adapter_sync_inc


def graph_sync_incremental(tenant_id: str) -> Dict[str, Any]:
    """Dispara sync incremental do tenant."""
    return adapter_sync_inc(tenant_id)

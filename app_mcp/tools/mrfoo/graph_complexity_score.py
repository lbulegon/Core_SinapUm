"""Tool mrfoo.graph.complexity_score — score de complexidade/NOG."""
from typing import Any, Dict

from adapters.mrfoo_adapter import complexity_score as adapter_complexity


def graph_complexity_score(tenant_id: str) -> Dict[str, Any]:
    """Retorna score de complexidade (NOG) do cardápio."""
    return adapter_complexity(tenant_id)

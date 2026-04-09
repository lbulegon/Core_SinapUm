"""Tool mrfoo.graph.new_item_suggestions — sugestões de novos itens."""
from typing import Any, Dict

from adapters.mrfoo_adapter import new_item_suggestions as adapter_new_items


def graph_new_item_suggestions(tenant_id: str, max_items: int = 10) -> Dict[str, Any]:
    """Retorna sugestões de novos itens para o cardápio."""
    return adapter_new_items(tenant_id, max_items)

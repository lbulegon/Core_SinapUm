# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.catalog_tool (via adapter)
# ============================================================================

from typing import Dict, Any, Optional
from adapters.vitrinezap_adapter import search_catalog, get_catalog_item


def catalog_search(shopper_id: str, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """Tool: Busca no catálogo (via vitrinezap_adapter)."""
    return search_catalog(shopper_id, query, filters)


def product_get(shopper_id: str, product_id: str) -> Dict[str, Any]:
    """Tool: Obtém produto (via vitrinezap_adapter)."""
    return get_catalog_item(shopper_id, product_id)


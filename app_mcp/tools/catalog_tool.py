# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.catalog_tool
# ============================================================================

from typing import Dict, Any, Optional
from ..clients import VitrineZapClient


def catalog_search(shopper_id: str, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Tool: Busca no catálogo
    
    Args:
        shopper_id: ID do Shopper
        query: Termo de busca
        filters: Filtros adicionais
    
    Returns:
        {
            'success': bool,
            'products': [...]
        }
    """
    client = VitrineZapClient()
    return client.search_catalog(shopper_id, query, filters)


def product_get(shopper_id: str, product_id: str) -> Dict[str, Any]:
    """
    Tool: Obtém produto
    
    Args:
        shopper_id: ID do Shopper
        product_id: ID do produto
    
    Returns:
        {
            'success': bool,
            'product': {...}
        }
    """
    client = VitrineZapClient()
    return client.get_product(shopper_id, product_id)


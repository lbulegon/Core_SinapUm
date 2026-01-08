# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.cart_tool
# ============================================================================

from typing import Dict, Any
from ..clients import VitrineZapClient


def cart_get(shopper_id: str, customer_id: str) -> Dict[str, Any]:
    """
    Tool: Obtém carrinho
    
    Args:
        shopper_id: ID do Shopper
        customer_id: ID do cliente
    
    Returns:
        {
            'success': bool,
            'cart': {...}
        }
    """
    client = VitrineZapClient()
    return client.get_cart(shopper_id, customer_id)


def cart_add(shopper_id: str, customer_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Tool: Adiciona produto ao carrinho
    
    Args:
        shopper_id: ID do Shopper
        customer_id: ID do cliente
        product_id: ID do produto
        quantity: Quantidade
    
    Returns:
        {
            'success': bool,
            'cart': {...}
        }
    """
    client = VitrineZapClient()
    return client.add_to_cart(shopper_id, customer_id, product_id, quantity)


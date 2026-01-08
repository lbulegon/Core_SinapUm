# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.order_tool
# ============================================================================

from typing import Dict, Any
from ..clients import VitrineZapClient


def order_create(shopper_id: str, customer_id: str, cart_id: str, address: Dict, payment_method: str) -> Dict[str, Any]:
    """
    Tool: Cria pedido
    
    Args:
        shopper_id: ID do Shopper
        customer_id: ID do cliente
        cart_id: ID do carrinho
        address: Endereço de entrega
        payment_method: Método de pagamento
    
    Returns:
        {
            'success': bool,
            'order_id': str,
            'order': {...}
        }
    """
    client = VitrineZapClient()
    return client.create_order(shopper_id, customer_id, cart_id, address, payment_method)


def order_status(shopper_id: str, order_id: str) -> Dict[str, Any]:
    """
    Tool: Obtém status do pedido
    
    Args:
        shopper_id: ID do Shopper
        order_id: ID do pedido
    
    Returns:
        {
            'success': bool,
            'status': str,
            'order': {...}
        }
    """
    client = VitrineZapClient()
    return client.get_order_status(shopper_id, order_id)


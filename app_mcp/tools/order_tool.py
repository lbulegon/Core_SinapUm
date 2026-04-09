# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.order_tool (via adapter)
# ============================================================================

from typing import Dict, Any
from adapters.vitrinezap_adapter import create_order, get_order


def order_create(shopper_id: str, customer_id: str, cart_id: str, address: Dict, payment_method: str) -> Dict[str, Any]:
    """Tool: Cria pedido (via vitrinezap_adapter)."""
    return create_order(shopper_id, customer_id, cart_id, address, payment_method)


def order_status(shopper_id: str, order_id: str) -> Dict[str, Any]:
    """Tool: Obtém status do pedido (via vitrinezap_adapter)."""
    return get_order(shopper_id, order_id)


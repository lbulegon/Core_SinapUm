# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.cart_tool (via adapter)
# ============================================================================

from typing import Dict, Any
from adapters.vitrinezap_adapter import get_cart, add_to_cart


def cart_get(shopper_id: str, customer_id: str) -> Dict[str, Any]:
    """Tool: Obtém carrinho (via vitrinezap_adapter)."""
    return get_cart(shopper_id, customer_id)


def cart_add(shopper_id: str, customer_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """Tool: Adiciona produto ao carrinho (via vitrinezap_adapter)."""
    return add_to_cart(shopper_id, customer_id, product_id, quantity)


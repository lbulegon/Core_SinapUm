# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.customer_tool (via adapter)
# ============================================================================

from typing import Dict, Any
from adapters.vitrinezap_adapter import get_customer


def customer_get_or_create(shopper_id: str, phone: str) -> Dict[str, Any]:
    """Tool: Obtém ou cria cliente (via vitrinezap_adapter)."""
    return get_customer(shopper_id, phone)


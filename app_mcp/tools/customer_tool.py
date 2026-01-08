# ============================================================================
# ARQUITETURA NOVA - app_mcp.tools.customer_tool
# ============================================================================

from typing import Dict, Any
from ..clients import VitrineZapClient


def customer_get_or_create(shopper_id: str, phone: str) -> Dict[str, Any]:
    """
    Tool: Obtém ou cria cliente
    
    Args:
        shopper_id: ID do Shopper
        phone: Telefone do cliente
    
    Returns:
        {
            'success': bool,
            'customer_id': str,
            'customer': {...}
        }
    """
    client = VitrineZapClient()
    return client.get_customer(shopper_id, phone)


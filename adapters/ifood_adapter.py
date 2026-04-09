"""
Adapter iFood — OAuth, pedidos, sincronização.
Delega para ifood_service ou endpoints Core (app_ifood_integration).
"""
from typing import Any, Dict, Optional

from .base import BaseAdapter


def get_order(order_id: str, **kwargs: Any) -> Dict[str, Any]:
    """Obtém pedido iFood. Stub."""
    return {"success": False, "error": "iFood adapter not implemented"}


class IfoodAdapter(BaseAdapter):
    """Adapter para Resources iFood (stub)."""

    def get(self, entity: str, id: Optional[str] = None, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

    def list(self, entity: str, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

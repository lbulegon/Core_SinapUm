"""
Adapter VitrineZap/Évora — catálogo, pedidos, carrinho, cliente.
Delega para app_mcp.clients.VitrineZapClient (sem duplicar lógica).
"""
from typing import Any, Dict, List, Optional

from .base import BaseAdapter


def get_client():
    """Retorna VitrineZapClient (lazy para evitar import circular)."""
    from app_mcp.clients import VitrineZapClient
    return VitrineZapClient()


def search_catalog(shopper_id: str, query: str = "", filters: Optional[Dict] = None) -> Dict[str, Any]:
    """Busca no catálogo."""
    return get_client().search_catalog(shopper_id, query, filters)


def get_catalog_item(shopper_id: str, product_id: str) -> Dict[str, Any]:
    """Obtém um item do catálogo (produto) por id."""
    return get_client().get_product(shopper_id, product_id)


def get_customer(shopper_id: str, phone: str) -> Dict[str, Any]:
    """Obtém ou cria cliente por telefone."""
    return get_client().get_customer(shopper_id, phone)


def get_cart(shopper_id: str, customer_id: str) -> Dict[str, Any]:
    """Obtém carrinho do cliente."""
    return get_client().get_cart(shopper_id, customer_id)


def add_to_cart(shopper_id: str, customer_id: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """Adiciona produto ao carrinho."""
    return get_client().add_to_cart(shopper_id, customer_id, product_id, quantity)


def create_order(
    shopper_id: str,
    customer_id: str,
    cart_id: str,
    address: Dict,
    payment_method: str = "pix",
) -> Dict[str, Any]:
    """Cria pedido."""
    return get_client().create_order(shopper_id, customer_id, cart_id, address, payment_method)


def get_order(shopper_id: str, order_id: str) -> Dict[str, Any]:
    """Obtém status do pedido."""
    return get_client().get_order_status(shopper_id, order_id)


class VitrineZapAdapter(BaseAdapter):
    """Adapter para Resources sinap://vitrinezap/*."""

    def get(
        self,
        entity: str,
        id: Optional[str] = None,
        query: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        query = query or {}
        shopper_id = query.get("shopper_id", "")
        if entity == "catalog" and id:
            out = get_catalog_item(shopper_id, id)
            return out if out.get("success") else None
        if entity == "orders" and id:
            out = get_order(shopper_id, id)
            return out if out.get("success") else None
        return None

    def list(
        self,
        entity: str,
        query: Optional[Dict[str, str]] = None,
    ) -> Optional[Dict[str, Any]]:
        query = query or {}
        shopper_id = query.get("shopper_id", "")
        q = query.get("q", "")
        if entity == "catalog":
            out = search_catalog(shopper_id, q)
            if not out.get("success"):
                return None
            return {"items": out.get("products", []), "total": len(out.get("products", []))}
        return None

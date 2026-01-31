"""
Cliente MCP - Chama tools do app_mcp no Core Django.
Permite ShopperBot executar ações: cart.add, catalog.search, order.create, etc.
"""
import httpx
import logging
from typing import Dict, Any, Optional
from app.utils.config import settings

logger = logging.getLogger(__name__)

# Mapeamento de tools app_mcp
TOOLS = [
    "customer.get_or_create",
    "catalog.search",
    "product.get",
    "cart.get",
    "cart.add",
    "order.create",
    "order.status",
]


def call_mcp_tool(
    tool_name: str,
    shopper_id: str,
    args: Optional[Dict[str, Any]] = None,
    timeout: float = 15.0,
) -> Dict[str, Any]:
    """
    Chama uma tool MCP no Core Django (app_mcp).
    
    Args:
        tool_name: Nome da tool (ex: catalog.search, cart.add)
        shopper_id: ID do Shopper
        args: Argumentos da tool (ex: {"query": "arroz", "filters": {}})
        timeout: Timeout em segundos
    
    Returns:
        dict: Resposta da tool {success, ...} ou {error, ...}
    
    Raises:
        ValueError: Se MCP desabilitado ou tool inválida
    """
    if not settings.MCP_ENABLED:
        raise ValueError("MCP está desabilitado (MCP_ENABLED=false)")
    
    if tool_name not in TOOLS:
        raise ValueError(f"Tool inválida: {tool_name}. Disponíveis: {TOOLS}")
    
    url = f"{settings.MCP_CORE_URL.rstrip('/')}/mcp/tools/{tool_name}"
    payload = {
        "shopper_id": shopper_id,
        "args": args or {},
    }
    
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPStatusError as e:
        logger.warning(f"MCP tool {tool_name} HTTP error: {e.response.status_code} - {e.response.text}")
        return {"success": False, "error": str(e), "status_code": e.response.status_code}
    except httpx.RequestError as e:
        logger.warning(f"MCP tool {tool_name} request error: {e}")
        return {"success": False, "error": str(e), "error_code": "CONNECTION_ERROR"}


def catalog_search(shopper_id: str, query: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
    """Busca no catálogo."""
    return call_mcp_tool("catalog.search", shopper_id, {"query": query, "filters": filters or {}})


def cart_add(
    shopper_id: str,
    customer_id: str,
    product_id: str,
    quantity: int = 1,
) -> Dict[str, Any]:
    """Adiciona produto ao carrinho."""
    return call_mcp_tool("cart.add", shopper_id, {
        "customer_id": customer_id,
        "product_id": product_id,
        "quantity": quantity,
    })


def cart_get(shopper_id: str, customer_id: str) -> Dict[str, Any]:
    """Obtém carrinho do cliente."""
    return call_mcp_tool("cart.get", shopper_id, {"customer_id": customer_id})


def order_create(
    shopper_id: str,
    customer_id: str,
    cart_id: str,
    address: Dict[str, Any],
    payment_method: str = "pix",
) -> Dict[str, Any]:
    """Cria pedido."""
    return call_mcp_tool("order.create", shopper_id, {
        "customer_id": customer_id,
        "cart_id": cart_id,
        "address": address,
        "payment_method": payment_method,
    })


def product_get(shopper_id: str, product_id: str) -> Dict[str, Any]:
    """Obtém produto por ID."""
    return call_mcp_tool("product.get", shopper_id, {"product_id": product_id})


def customer_get_or_create(shopper_id: str, phone: str) -> Dict[str, Any]:
    """Obtém ou cria cliente pelo telefone."""
    return call_mcp_tool("customer.get_or_create", shopper_id, {"phone": phone})


def order_status(shopper_id: str, order_id: str) -> Dict[str, Any]:
    """Consulta status do pedido."""
    return call_mcp_tool("order.status", shopper_id, {"order_id": order_id})

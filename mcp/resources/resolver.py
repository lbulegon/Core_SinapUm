"""
Resolver de MCP Resources (sinap://).

Resolve URIs sinap://{vertical}/{entity}/{id} usando adapters.
Se o adapter não existir, retorna None (caller pode 404).
Não altera comportamento de endpoints existentes.
"""
import logging
from typing import Any, Callable, Dict, List, Optional

from mcp.uri import SinapURI, parse_sinap_uri
from .schemas import ResourceResult, ResourceListResult

logger = logging.getLogger(__name__)

# Registry: (vertical, entity) -> callable get, callable list (opcional)
_resource_handlers: Dict[tuple, Dict[str, Any]] = {}


def register_resource_handler(
    vertical: str,
    entity: str,
    get_fn: Optional[Callable[..., Optional[ResourceResult]]] = None,
    list_fn: Optional[Callable[..., Optional[ResourceListResult]]] = None,
) -> None:
    """Registra handler para vertical/entity. Chamado pelos adapters ao carregar."""
    key = (vertical.lower(), entity.lower())
    _resource_handlers[key] = {"get": get_fn, "list": list_fn}
    logger.debug("Registered resource handler %s/%s", vertical, entity)


def _get_handler(vertical: str, entity: str, op: str) -> Optional[Callable]:
    key = (vertical.lower(), entity.lower())
    entry = _resource_handlers.get(key)
    if not entry:
        return None
    return entry.get(op)


def resolve_resource(uri: str) -> Optional[ResourceResult]:
    """
    Resolve um resource por URI (get por id).
    sinap://vitrinezap/catalog/123 -> ResourceResult com dados do catalog 123.

    Returns:
        ResourceResult se encontrado, None se URI inválida ou adapter não registrado.
    """
    parsed = parse_sinap_uri(uri)
    if not parsed:
        return None
    handler = _get_handler(parsed.vertical, parsed.entity, "get")
    if not handler:
        logger.debug("No get handler for %s/%s", parsed.vertical, parsed.entity)
        return None
    try:
        return handler(parsed)
    except Exception as e:
        logger.warning("Resource get failed for %s: %s", uri, e)
        return None


def list_resources(
    uri: str,
    query: Optional[Dict[str, str]] = None,
) -> Optional[ResourceListResult]:
    """
    Lista resources por URI base (sem id).
    sinap://vitrinezap/catalog?limit=10 -> ResourceListResult com itens.

    Returns:
        ResourceListResult se handler existir, None caso contrário.
    """
    parsed = parse_sinap_uri(uri)
    if not parsed:
        return None
    handler = _get_handler(parsed.vertical, parsed.entity, "list")
    if not handler:
        logger.debug("No list handler for %s/%s", parsed.vertical, parsed.entity)
        return None
    query = query or (parsed.query or {})
    try:
        return handler(parsed, query)
    except Exception as e:
        logger.warning("Resource list failed for %s: %s", uri, e)
        return None


def get_registered_handlers() -> Dict[str, List[str]]:
    """Retorna vertical -> [entity] registrados (para documentação/health)."""
    out: Dict[str, List[str]] = {}
    for (v, e) in _resource_handlers:
        out.setdefault(v, []).append(e)
    return out

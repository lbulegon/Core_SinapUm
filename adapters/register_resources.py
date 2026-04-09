"""
Registra handlers MCP Resources (sinap://) usando os adapters.
Chamado no AppConfig.ready do app_mcp_tool_registry.
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _get_vitrinezap(parsed) -> Optional["ResourceResult"]:
    from mcp.resources.schemas import ResourceResult
    from .vitrinezap_adapter import VitrineZapAdapter
    adapter = VitrineZapAdapter()
    query = dict(parsed.query or {})
    data = adapter.get(parsed.entity, parsed.id, query)
    if data is None:
        return None
    return ResourceResult(uri=parsed.raw or str(parsed), data=data)


def _list_vitrinezap(parsed, query: Dict) -> Optional["ResourceListResult"]:
    from mcp.resources.schemas import ResourceListResult
    from .vitrinezap_adapter import VitrineZapAdapter
    adapter = VitrineZapAdapter()
    q = dict(query)
    out = adapter.list(parsed.entity, q)
    if out is None:
        return None
    return ResourceListResult(
        uri=parsed.raw or str(parsed),
        items=out.get("items", []),
        total=out.get("total"),
    )


def _get_motopro(parsed) -> Optional["ResourceResult"]:
    from mcp.resources.schemas import ResourceResult
    from .motopro_adapter import MotoProAdapter
    adapter = MotoProAdapter()
    data = adapter.get(parsed.entity, parsed.id, parsed.query)
    if data is None:
        return None
    return ResourceResult(uri=parsed.raw or str(parsed), data=data)


def _get_mrfoo(parsed) -> Optional["ResourceResult"]:
    from mcp.resources.schemas import ResourceResult
    from .mrfoo_adapter import MrFooAdapter
    adapter = MrFooAdapter()
    data = adapter.get(parsed.entity, parsed.id, parsed.query)
    if data is None:
        return None
    return ResourceResult(uri=parsed.raw or str(parsed), data=data)


def register_all_resource_handlers() -> None:
    """Registra handlers sinap:// para vitrinezap, motopro, mrfoo."""
    try:
        from mcp.resources.resolver import register_resource_handler
        register_resource_handler("vitrinezap", "catalog", get_fn=_get_vitrinezap, list_fn=_list_vitrinezap)
        register_resource_handler("vitrinezap", "orders", get_fn=_get_vitrinezap, list_fn=None)
        register_resource_handler("motopro", "orders", get_fn=_get_motopro, list_fn=None)
        register_resource_handler("mrfoo", "menu", get_fn=_get_mrfoo, list_fn=None)
        register_resource_handler("mrfoo", "graph", get_fn=_get_mrfoo, list_fn=None)
        logger.info("MCP Resources handlers registered (vitrinezap, motopro, mrfoo)")
    except Exception as e:
        logger.warning("Could not register MCP resource handlers: %s", e)

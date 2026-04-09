"""
MCP Resources — resolver sinap:// usando adapters.

Uso:
  from mcp.resources import resolve_resource, list_resources
"""
from .resolver import resolve_resource, list_resources, get_registered_handlers, register_resource_handler
from .schemas import ResourceResult, ResourceListResult

__all__ = [
    "resolve_resource",
    "list_resources",
    "get_registered_handlers",
    "register_resource_handler",
    "ResourceResult",
    "ResourceListResult",
]

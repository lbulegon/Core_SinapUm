"""
Schemas para MCP Resources (sinap://).
"""
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class ResourceResult:
    """Resultado de um resource get (um item)."""
    uri: str
    data: Dict[str, Any]
    content_type: str = "application/json"
    meta: Optional[Dict[str, Any]] = None


@dataclass
class ResourceListResult:
    """Resultado de list/search (múltiplos itens)."""
    uri: str
    items: List[Dict[str, Any]]
    total: Optional[int] = None
    next_cursor: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

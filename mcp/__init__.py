"""
MCP — Model Context Protocol (convenção Core_SinapUm).

Utilitários: URI sinap://, Resources resolver.
Implementações reais: app_mcp_tool_registry, app_mcp, services/mcp_service.
"""
from mcp.uri import SinapURI, parse_sinap_uri, is_sinap_uri, validate_sinap_uri

__all__ = ["SinapURI", "parse_sinap_uri", "is_sinap_uri", "validate_sinap_uri"]

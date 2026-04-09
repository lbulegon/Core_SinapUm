"""
MCP Adapter - Integração com Model Context Protocol do Core.

ADAPTAR: Chamar MCP Service (porta 7010) para tools architecture.*
Por ora, stub para futura integração.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class MCPAdapter(ABC):
    """Interface para chamadas MCP"""

    @abstractmethod
    def call_tool(self, tool: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Chama tool no MCP Service"""
        pass


class StubMCPAdapter(MCPAdapter):
    """Stub - retorna resposta vazia"""

    def call_tool(self, tool: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"ok": False, "message": "MCP adapter not configured"}

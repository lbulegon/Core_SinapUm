"""
MCP Client - Conecta DDF a servidores MCP externos
Permite que o DDF use ferramentas externas (Git, Jira, Figma, etc.)
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:
    """Cliente MCP para conectar a servidores externos"""
    
    def __init__(self, server_name: str, command: List[str], env: Optional[Dict] = None):
        """
        Inicializa cliente MCP
        
        Args:
            server_name: Nome do servidor MCP
            command: Comando para iniciar servidor
            env: Variáveis de ambiente (opcional)
        """
        self.server_name = server_name
        self.server_params = StdioServerParameters(
            command=command[0],
            args=command[1:] if len(command) > 1 else [],
            env=env or {}
        )
        self.session: Optional[ClientSession] = None
    
    async def connect(self):
        """Conecta ao servidor MCP"""
        self.session = await stdio_client(self.server_params)
        await self.session.initialize()
    
    async def list_tools(self) -> List[Dict]:
        """Lista ferramentas disponíveis no servidor"""
        if not self.session:
            await self.connect()
        
        tools = await self.session.list_tools()
        return [tool.model_dump() for tool in tools.tools]
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chama uma ferramenta do servidor MCP"""
        if not self.session:
            await self.connect()
        
        result = await self.session.call_tool(tool_name, arguments)
        return result
    
    async def disconnect(self):
        """Desconecta do servidor MCP"""
        if self.session:
            await self.session.__aexit__(None, None, None)
            self.session = None


class MCPManager:
    """Gerencia múltiplos clientes MCP"""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
    
    def register_client(self, name: str, client: MCPClient):
        """Registra um cliente MCP"""
        self.clients[name] = client
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Chama ferramenta em um servidor MCP específico"""
        if server_name not in self.clients:
            raise ValueError(f"Servidor MCP '{server_name}' não registrado")
        
        client = self.clients[server_name]
        return await client.call_tool(tool_name, arguments)
    
    async def list_all_tools(self) -> Dict[str, List[Dict]]:
        """Lista todas as ferramentas de todos os servidores"""
        all_tools = {}
        
        for name, client in self.clients.items():
            try:
                tools = await client.list_tools()
                all_tools[name] = tools
            except Exception as e:
                all_tools[name] = [{"error": str(e)}]
        
        return all_tools


# Exemplos de configuração de servidores MCP
MCP_SERVERS = {
    "git": {
        "command": ["npx", "-y", "@modelcontextprotocol/server-git"],
        "env": {}
    },
    "filesystem": {
        "command": ["npx", "-y", "@modelcontextprotocol/server-filesystem"],
        "env": {"ALLOWED_DIRECTORIES": "/root/ddf"}
    },
    "postgres": {
        "command": ["python", "-m", "mcp_server_postgres"],
        "env": {
            "POSTGRES_URL": "postgresql://ddf:ddf@postgres:5432/ddf"
        }
    }
}


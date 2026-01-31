#!/usr/bin/env python3
"""
MCP Server via stdio - Expõe tools do Core SinapUm para clientes MCP (Claude Desktop, Cursor).

Uso:
  python run_mcp_stdio.py

Ou no Claude Desktop claude_desktop_config.json:
  {
    "mcpServers": {
      "sinapum": {
        "command": "python",
        "args": ["/caminho/para/run_mcp_stdio.py"],
        "env": {
          "MCP_SERVICE_URL": "http://localhost:7010"
        }
      }
    }
  }
"""
import asyncio
import json
import os
import sys

MCP_SERVICE_URL = os.getenv("MCP_SERVICE_URL", "http://localhost:7010")


def _fetch_tools():
    """Busca tools do MCP Service."""
    try:
        import requests
        r = requests.get(f"{MCP_SERVICE_URL}/mcp/tools", timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


def _call_tool(tool: str, input_data: dict, api_key: str = None):
    """Chama tool no MCP Service."""
    try:
        import requests
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-SINAPUM-KEY"] = api_key
        r = requests.post(
            f"{MCP_SERVICE_URL}/mcp/call",
            json={"tool": tool, "input": input_data},
            headers=headers,
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    """Entrypoint síncrono - tenta usar mcp package para stdio."""
    try:
        from mcp.server.lowlevel import Server
        from mcp.server.stdio import stdio_server
        import anyio
    except ImportError:
        print(
            "MCP SDK não instalado. Execute: pip install mcp",
            file=sys.stderr,
        )
        sys.exit(1)

    api_key = os.getenv("SINAPUM_API_KEY", "")

    server = Server("sinapum-mcp")

    try:
        from mcp.types import Tool, TextContent
    except ImportError:
        Tool = dict
        TextContent = lambda **kw: kw

    @server.list_tools()
    async def list_tools():
        tools_data = _fetch_tools()
        result = []
        for t in (tools_data if isinstance(tools_data, list) else []):
            name = t.get("name", "")
            desc = t.get("description", "Tool SinapUm")
            if isinstance(Tool, type):
                result.append(Tool(name=name, description=desc, inputSchema={"type": "object"}))
            else:
                result.append({"name": name, "description": desc, "inputSchema": {"type": "object"}})
        if not result:
            default = "vitrinezap.analisar_produto"
            if isinstance(Tool, type):
                result = [Tool(name=default, description="Analisa imagem de produto", inputSchema={"type": "object"})]
            else:
                result = [{"name": default, "description": "Analisa imagem de produto", "inputSchema": {"type": "object"}}]
        return result

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        inp = arguments.get("input", arguments)
        result = _call_tool(name, inp, api_key)
        text = json.dumps(result if not result.get("ok") else result.get("output", result), ensure_ascii=False)
        if isinstance(TextContent, type):
            return [TextContent(type="text", text=text)]
        return [{"type": "text", "text": text}]

    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    anyio.run(run)


if __name__ == "__main__":
    main()

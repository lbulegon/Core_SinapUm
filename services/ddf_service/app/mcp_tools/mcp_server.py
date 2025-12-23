"""
MCP Server - Expõe DDF como servidor MCP
Permite que Claude Code e outros clientes MCP usem o DDF
"""

import asyncio
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import Tool, TextContent
from mcp.types import Tool as MCPTool

from app.core.detect import detect_task
from app.core.delegate import delegate_task
from app.providers.provider_factory import ProviderFactory
from app.core.registry import REGISTRY


class DDFMCPServer:
    """Servidor MCP que expõe capacidades do DDF"""
    
    def __init__(self):
        self.server = Server("ddf-server")
        self._register_tools()
    
    def _register_tools(self):
        """Registra ferramentas MCP do DDF"""
        
        @self.server.list_tools()
        async def list_tools() -> List[MCPTool]:
            """Lista todas as ferramentas disponíveis"""
            return [
                MCPTool(
                    name="ddf_detect",
                    description="Classifica uma tarefa em categoria e intenção",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Texto da tarefa a ser classificada"
                            },
                            "context": {
                                "type": "object",
                                "description": "Contexto adicional (opcional)"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                MCPTool(
                    name="ddf_execute",
                    description="Executa tarefa completa: detecta, delega e executa",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Texto da tarefa"
                            },
                            "provider": {
                                "type": "string",
                                "description": "Provider específico (opcional)"
                            },
                            "context": {
                                "type": "object",
                                "description": "Contexto adicional"
                            }
                        },
                        "required": ["text"]
                    }
                ),
                MCPTool(
                    name="ddf_list_categories",
                    description="Lista todas as categorias de IA disponíveis",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                MCPTool(
                    name="ddf_list_providers",
                    description="Lista providers disponíveis para uma categoria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "description": "Categoria de IA"
                            }
                        },
                        "required": ["category"]
                    }
                ),
                MCPTool(
                    name="ddf_generate_text",
                    description="Gera texto usando IA apropriada",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Prompt para geração de texto"
                            },
                            "provider": {
                                "type": "string",
                                "description": "Provider específico (opcional)"
                            }
                        },
                        "required": ["prompt"]
                    }
                ),
                MCPTool(
                    name="ddf_generate_image",
                    description="Gera imagem usando IA apropriada",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "Prompt para geração de imagem"
                            },
                            "width": {
                                "type": "integer",
                                "description": "Largura da imagem (opcional)"
                            },
                            "height": {
                                "type": "integer",
                                "description": "Altura da imagem (opcional)"
                            }
                        },
                        "required": ["prompt"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Executa ferramenta MCP"""
            
            if name == "ddf_detect":
                text = arguments.get("text", "")
                context = arguments.get("context", {})
                detection = detect_task(text, context)
                return [TextContent(
                    type="text",
                    text=f"Detecção: {detection}"
                )]
            
            elif name == "ddf_execute":
                text = arguments.get("text", "")
                provider_override = arguments.get("provider")
                context = arguments.get("context", {})
                
                # Detect
                detection = detect_task(text, context)
                
                # Delegate
                delegation = delegate_task(detection, context)
                
                # Execute
                provider_name = provider_override or delegation.get('primary_provider')
                provider = ProviderFactory.create(provider_name, context.get('provider_configs', {}).get(provider_name, {}))
                
                if not provider.is_available():
                    return [TextContent(
                        type="text",
                        text=f"Erro: Provider '{provider_name}' não disponível"
                    )]
                
                result = provider.execute(text, **arguments.get('params', {}))
                
                return [TextContent(
                    type="text",
                    text=f"Resultado: {result}"
                )]
            
            elif name == "ddf_list_categories":
                categories = REGISTRY.get_all_categories()
                return [TextContent(
                    type="text",
                    text=f"Categorias disponíveis: {', '.join(categories)}"
                )]
            
            elif name == "ddf_list_providers":
                category = arguments.get("category", "")
                providers = REGISTRY.get_providers_by_category(category)
                return [TextContent(
                    type="text",
                    text=f"Providers para '{category}': {', '.join(providers)}"
                )]
            
            elif name == "ddf_generate_text":
                prompt = arguments.get("prompt", "")
                provider_override = arguments.get("provider")
                
                detection = detect_task(prompt, {"intent": "gerar"})
                detection["category"] = "escrita"  # Forçar categoria escrita
                
                delegation = delegate_task(detection, {})
                provider_name = provider_override or delegation.get('primary_provider')
                provider = ProviderFactory.create(provider_name, {})
                
                result = provider.execute(prompt)
                return [TextContent(
                    type="text",
                    text=result.get('output', str(result))
                )]
            
            elif name == "ddf_generate_image":
                prompt = arguments.get("prompt", "")
                width = arguments.get("width", 1024)
                height = arguments.get("height", 1024)
                
                detection = detect_task(prompt, {"intent": "gerar"})
                detection["category"] = "imagem"  # Forçar categoria imagem
                
                delegation = delegate_task(detection, {})
                provider_name = delegation.get('primary_provider')
                provider = ProviderFactory.create(provider_name, {})
                
                result = provider.execute(prompt, width=width, height=height)
                return [TextContent(
                    type="text",
                    text=f"Imagem gerada: {result.get('output', {}).get('image_url', 'N/A')}"
                )]
            
            else:
                return [TextContent(
                    type="text",
                    text=f"Ferramenta '{name}' não encontrada"
                )]
    
    async def run(self, transport):
        """Executa servidor MCP"""
        await self.server.run(transport)


# Instância global
mcp_server = DDFMCPServer()


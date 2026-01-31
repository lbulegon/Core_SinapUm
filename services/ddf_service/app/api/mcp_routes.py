"""
Rotas MCP - Expõe DDF como servidor MCP via HTTP REST.
Permite clientes MCP (Claude Code, Cursor, etc.) chamarem tools do DDF.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from app.core.detect import detect_task
from app.core.delegate import delegate_task
from app.core.registry import REGISTRY
from app.providers.provider_factory import ProviderFactory

router = APIRouter(tags=["DDF MCP"])

# Definições das tools MCP do DDF
MCP_TOOLS = [
    {
        "name": "ddf_detect",
        "description": "Classifica uma tarefa em categoria e intenção",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto da tarefa"},
                "context": {"type": "object", "description": "Contexto adicional"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "ddf_execute",
        "description": "Executa tarefa completa: detecta, delega e executa",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto da tarefa"},
                "provider": {"type": "string", "description": "Provider específico (opcional)"},
                "context": {"type": "object", "description": "Contexto adicional"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "ddf_list_categories",
        "description": "Lista todas as categorias de IA disponíveis",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "ddf_list_providers",
        "description": "Lista providers disponíveis para uma categoria",
        "inputSchema": {
            "type": "object",
            "properties": {"category": {"type": "string"}},
            "required": ["category"],
        },
    },
]




@router.get("/tools")
async def list_tools():
    """Lista tools MCP do DDF (compatível com MCP protocol)"""
    return {"tools": MCP_TOOLS}


@router.post("/call")
async def call_tool(request: Dict[str, Any]):
    """
    Executa tool MCP.
    Body: {"tool": "ddf_detect", "arguments": {"text": "...", "context": {}}}
    """
    tool_name = request.get("tool") or request.get("name")
    arguments = request.get("arguments") or request.get("input") or {}
    
    if not tool_name:
        raise HTTPException(status_code=400, detail="Campo 'tool' ou 'name' é obrigatório")
    
    if tool_name == "ddf_detect":
        text = arguments.get("text", "")
        context = arguments.get("context", {})
        detection = detect_task(text, context)
        return {"success": True, "output": {"detection": detection}}
    
    elif tool_name == "ddf_execute":
        text = arguments.get("text", "")
        provider_override = arguments.get("provider")
        context = arguments.get("context", {})
        
        detection = detect_task(text, context)
        delegation = delegate_task(detection, context)
        provider_name = provider_override or delegation.get("primary_provider")
        provider = ProviderFactory.create(provider_name, context.get("provider_configs", {}).get(provider_name, {}))
        
        if not provider.is_available():
            raise HTTPException(
                status_code=503,
                detail=f"Provider '{provider_name}' não disponível"
            )
        
        result = provider.execute(text, **arguments.get("params", {}))
        return {
            "success": True,
            "output": {
                "detection": detection,
                "delegation": delegation,
                "result": result,
            },
        }
    
    elif tool_name == "ddf_list_categories":
        categories = REGISTRY.get_all_categories()
        return {"success": True, "output": {"categories": categories}}
    
    elif tool_name == "ddf_list_providers":
        category = arguments.get("category", "")
        providers = REGISTRY.get_providers_by_category(category)
        return {"success": True, "output": {"category": category, "providers": providers}}
    
    else:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' não encontrada")

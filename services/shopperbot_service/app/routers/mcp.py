"""Router para ações MCP (cart, catalog, order)"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from app.services.mcp_client import call_mcp_tool, TOOLS
from app.utils.config import settings
from app.utils.logging import logger, get_request_id

router = APIRouter(prefix="/v1/mcp", tags=["mcp"])


class MCPCallRequest(BaseModel):
    """Request para chamar tool MCP"""
    tool_name: str = Field(..., description="Nome da tool (ex: catalog.search, cart.add)")
    shopper_id: str = Field(..., description="ID do Shopper")
    args: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Argumentos da tool")


class MCPCallResponse(BaseModel):
    """Response da chamada MCP"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    tool_name: str
    shopper_id: str


@router.get("/tools")
async def list_mcp_tools():
    """Lista tools MCP disponíveis"""
    return {
        "tools": TOOLS,
        "mcp_enabled": settings.MCP_ENABLED,
        "core_url": settings.MCP_CORE_URL if settings.MCP_ENABLED else None,
    }


@router.post("/call", response_model=MCPCallResponse)
async def call_tool(request: MCPCallRequest):
    """
    Chama uma tool MCP no Core (app_mcp).
    Requer FEATURE_EVOLUTION_MULTI_TENANT=true no Core para /mcp/tools estar disponível.
    """
    if not settings.MCP_ENABLED:
        raise HTTPException(
            status_code=503,
            detail="MCP está desabilitado. Defina MCP_ENABLED=true."
        )
    
    try:
        result = call_mcp_tool(
            tool_name=request.tool_name,
            shopper_id=request.shopper_id,
            args=request.args or {},
        )
        
        success = result.get("success", False)
        return MCPCallResponse(
            success=success,
            data=result,
            error=result.get("error") if not success else None,
            tool_name=request.tool_name,
            shopper_id=request.shopper_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao chamar MCP tool {request.tool_name}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

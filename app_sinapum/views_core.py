"""
Core Registry Views - Django
Endpoints para gerenciar tools versionadas (MCP Registry).

O Core Registry é a autoridade central para:
- Listar tools disponíveis
- Resolver tools (versão, schema, runtime, config)
- Versionamento de tools
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

# ============================================================================
# Registry de Tools (Hardcoded inicialmente - MVP)
# ============================================================================

# TODO: Migrar para banco de dados futuramente
TOOLS_REGISTRY = [
    {
        "name": "vitrinezap.analisar_produto",
        "version": "1.0.0",
        "description": "Analisa produto e retorna JSON estruturado",
        "enabled": True
    },
    {
        "name": "vitrinezap.analisar_produto",
        "version": "1.1.0",
        "description": "Analisa produto com melhorias (versão mais recente)",
        "enabled": True
    },
    {
        "name": "vitrinezap.extrair_caracteristicas",
        "version": "1.0.0",
        "description": "Extrai características de produto",
        "enabled": True
    }
]

# Configurações de resolução de tools
TOOLS_RESOLUTION = {
    "vitrinezap.analisar_produto": {
        "1.0.0": {
            "runtime": "agno",
            "config": {
                "model": "gpt-4.1",
                "temperature": 0.2
            },
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string"},
                    "language": {"type": "string", "default": "pt-BR"}
                },
                "required": ["image_url"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "descricao": {"type": "string"},
                    "preco": {"type": "number"},
                    "categoria": {"type": "string"}
                }
            },
            "prompt_ref": "PROMPT_ANALISE_PRODUTO_V1"
        },
        "1.1.0": {
            "runtime": "agno",
            "config": {
                "model": "gpt-4.1",
                "temperature": 0.1
            },
            "input_schema": {
                "type": "object",
                "properties": {
                    "image_url": {"type": "string"},
                    "language": {"type": "string", "default": "pt-BR"},
                    "detailed": {"type": "boolean", "default": True}
                },
                "required": ["image_url"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "descricao": {"type": "string"},
                    "preco": {"type": "number"},
                    "categoria": {"type": "string"},
                    "caracteristicas": {"type": "array"}
                }
            },
            "prompt_ref": "PROMPT_ANALISE_PRODUTO_V2"
        }
    },
    "vitrinezap.extrair_caracteristicas": {
        "1.0.0": {
            "runtime": "openmind",
            "config": {
                "model": "gpt-4o",
                "temperature": 0.3
            },
            "input_schema": {
                "type": "object",
                "properties": {
                    "product_data": {"type": "object"}
                },
                "required": ["product_data"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "caracteristicas": {"type": "array"}
                }
            },
            "prompt_ref": "PROMPT_EXTRAIR_CARACTERISTICAS_V1"
        }
    }
}

# ============================================================================
# Endpoints
# ============================================================================

@require_http_methods(["GET"])
def list_tools(request):
    """
    GET /core/tools
    
    Lista todas as tools disponíveis no registry.
    
    Returns:
        JSON array com tools disponíveis
    """
    try:
        logger.info("Listando tools do registry")
        
        # Filtrar apenas tools habilitadas
        enabled_tools = [tool for tool in TOOLS_REGISTRY if tool.get("enabled", True)]
        
        return JsonResponse(enabled_tools, safe=False)
    
    except Exception as e:
        logger.error(f"Erro ao listar tools: {e}")
        return JsonResponse(
            {"error": "Erro ao listar tools", "detail": str(e)},
            status=500
        )

@csrf_exempt
@require_http_methods(["POST"])
def resolve_tool(request):
    """
    POST /core/tools/resolve
    
    Resolve uma tool específica, retornando:
    - Versão
    - Runtime (agno, openmind, etc)
    - Configuração (model, temperature, etc)
    - Schemas de input/output
    - Referência ao prompt
    
    Body:
        {
            "tool": "vitrinezap.analisar_produto",
            "version": "1.0.0",
            "input": { ... }
        }
    
    Returns:
        JSON com plano de execução da tool
    """
    try:
        # Parse do body
        body = json.loads(request.body)
        tool_name = body.get("tool")
        version = body.get("version")
        input_data = body.get("input", {})
        
        logger.info(f"Resolvendo tool: {tool_name} v{version}")
        
        if not tool_name or not version:
            return JsonResponse(
                {"error": "tool e version são obrigatórios"},
                status=400
            )
        
        # Buscar resolução da tool
        tool_resolutions = TOOLS_RESOLUTION.get(tool_name)
        if not tool_resolutions:
            logger.warning(f"Tool não encontrada: {tool_name}")
            return JsonResponse(
                {"error": f"Tool '{tool_name}' não encontrada no registry"},
                status=404
            )
        
        # Buscar versão específica
        resolution = tool_resolutions.get(version)
        if not resolution:
            logger.warning(f"Versão não encontrada: {tool_name} v{version}")
            return JsonResponse(
                {"error": f"Versão '{version}' não encontrada para tool '{tool_name}'"},
                status=404
            )
        
        # Montar resposta com plano de execução
        execution_plan = {
            "tool": tool_name,
            "version": version,
            "runtime": resolution.get("runtime"),
            "config": resolution.get("config", {}),
            "input_schema": resolution.get("input_schema", {}),
            "output_schema": resolution.get("output_schema", {}),
            "prompt_ref": resolution.get("prompt_ref")
        }
        
        logger.info(f"Plano de execução gerado para {tool_name} v{version}")
        
        return JsonResponse(execution_plan)
    
    except json.JSONDecodeError:
        logger.error("Erro ao parsear JSON do body")
        return JsonResponse(
            {"error": "Body inválido. Esperado JSON."},
            status=400
        )
    except Exception as e:
        logger.error(f"Erro ao resolver tool: {e}")
        return JsonResponse(
            {"error": "Erro ao resolver tool", "detail": str(e)},
            status=500
        )

@require_http_methods(["GET"])
def health_check(request):
    """
    GET /health
    
    Health check do Core Registry.
    """
    return JsonResponse({
        "status": "healthy",
        "service": "core_registry",
        "tools_count": len([t for t in TOOLS_REGISTRY if t.get("enabled", True)])
    })


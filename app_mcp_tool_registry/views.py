"""
Views para o MCP Tool Registry
"""
import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from .models import ClientApp, Tool, ToolVersion, ToolCallLog
from .utils import resolve_prompt_from_ref

logger = logging.getLogger(__name__)


def get_client_from_api_key(request):
    """
    Helper para obter ClientApp a partir do header X-SINAPUM-KEY
    
    Returns:
        ClientApp ou None se inválido/ausente
    """
    api_key = request.headers.get('X-SINAPUM-KEY', '')
    if not api_key:
        return None
    
    try:
        client = ClientApp.objects.get(api_key=api_key, is_active=True)
        return client
    except ClientApp.DoesNotExist:
        return None


@require_http_methods(["GET"])
def list_tools(request):
    """
    GET /core/tools/
    
    Lista todas as tools ativas com current_version.
    """
    try:
        tools = Tool.objects.filter(is_active=True).select_related('current_version')
        
        tools_list = []
        for tool in tools:
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "current_version": tool.current_version.version if tool.current_version else None,
                "is_active": tool.is_active
            })
        
        return JsonResponse(tools_list, safe=False)
    
    except Exception as e:
        logger.error(f"Erro ao listar tools: {e}")
        return JsonResponse(
            {"error": "Erro ao listar tools", "detail": str(e)},
            status=500
        )


@require_http_methods(["GET"])
def get_tool_detail(request, tool_name):
    """
    GET /core/tools/<tool_name>/
    
    Retorna detalhes da tool com suas versões.
    """
    try:
        tool = get_object_or_404(Tool, name=tool_name)
        
        versions = tool.versions.all().order_by('-created_at')
        versions_list = []
        for version in versions:
            versions_list.append({
                "version": version.version,
                "runtime": version.runtime,
                "is_active": version.is_active,
                "is_deprecated": version.is_deprecated
            })
        
        return JsonResponse({
            "name": tool.name,
            "description": tool.description,
            "is_active": tool.is_active,
            "current_version": tool.current_version.version if tool.current_version else None,
            "versions": versions_list
        })
    
    except Tool.DoesNotExist:
        return JsonResponse(
            {"error": f"Tool '{tool_name}' não encontrada"},
            status=404
        )
    except Exception as e:
        logger.error(f"Erro ao buscar tool {tool_name}: {e}")
        return JsonResponse(
            {"error": "Erro ao buscar tool", "detail": str(e)},
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def resolve_tool(request):
    """
    POST /core/tools/resolve/
    
    Resolve uma tool e retorna o ToolVersion completo.
    Aceita client_key no body ou infere via API key.
    """
    try:
        # Parse do body
        body = json.loads(request.body)
        tool_name = body.get("tool")
        version_str = body.get("version")
        client_key = body.get("client_key")
        input_data = body.get("input", {})
        
        if not tool_name:
            return JsonResponse(
                {"error": "tool é obrigatório"},
                status=400
            )
        
        # Obter cliente (via API key ou client_key)
        client = None
        if client_key:
            try:
                client = ClientApp.objects.get(key=client_key, is_active=True)
            except ClientApp.DoesNotExist:
                return JsonResponse(
                    {"error": f"ClientApp '{client_key}' não encontrado ou inativo"},
                    status=404
                )
        else:
            # Tentar inferir via API key
            client = get_client_from_api_key(request)
            if not client:
                return JsonResponse(
                    {"error": "API key inválida ou ausente. Forneça X-SINAPUM-KEY ou client_key no body."},
                    status=401
                )
        
        # Buscar tool
        try:
            tool = Tool.objects.get(name=tool_name)
        except Tool.DoesNotExist:
            return JsonResponse(
                {"error": f"Tool '{tool_name}' não encontrada"},
                status=404
            )
        
        # Verificar se tool está ativa
        if not tool.is_active:
            return JsonResponse(
                {"error": f"Tool '{tool_name}' está inativa"},
                status=403
            )
        
        # Verificar permissão (allowed_clients)
        if tool.allowed_clients.exists():
            if client not in tool.allowed_clients.all():
                return JsonResponse(
                    {"error": f"Cliente '{client.key}' não tem permissão para usar esta tool"},
                    status=403
                )
        
        # Buscar versão (se não veio, usa current)
        if version_str:
            try:
                tool_version = ToolVersion.objects.get(
                    tool=tool,
                    version=version_str,
                    is_active=True
                )
            except ToolVersion.DoesNotExist:
                return JsonResponse(
                    {"error": f"Versão '{version_str}' não encontrada ou inativa para tool '{tool_name}'"},
                    status=404
                )
        else:
            # Usar versão atual
            if not tool.current_version:
                return JsonResponse(
                    {"error": f"Tool '{tool_name}' não tem versão atual definida"},
                    status=404
                )
            tool_version = tool.current_version
        
        # Resolver prompt_ref para texto do prompt (se existir)
        # Usa múltiplas fontes: PostgreSQL, URLs, inline no config
        prompt_text = None
        if tool_version.prompt_ref or (tool_version.config and tool_version.config.get("prompt_inline")):
            prompt_text = resolve_prompt_from_ref(
                tool_version.prompt_ref,
                config=tool_version.config
            )
            if prompt_text:
                logger.info(f"✅ Prompt resolvido para tool {tool.name}@{tool_version.version} (fonte: {tool_version.prompt_ref or 'inline'})")
            else:
                logger.warning(f"⚠️ Prompt_ref '{tool_version.prompt_ref}' não pôde ser resolvido para tool {tool.name}@{tool_version.version}")
        
        # Retornar ToolVersion completo
        execution_plan = {
            "tool": tool.name,
            "version": tool_version.version,
            "runtime": tool_version.runtime,
            "config": tool_version.config,
            "input_schema": tool_version.input_schema,
            "output_schema": tool_version.output_schema,
            "prompt_ref": tool_version.prompt_ref,
            "prompt_text": prompt_text,  # Texto do prompt resolvido (se disponível)
            "client_key": client.key  # Incluir client_key na resposta
        }
        
        return JsonResponse(execution_plan)
    
    except json.JSONDecodeError:
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


@csrf_exempt
@require_http_methods(["POST"])
def log_tool_call(request):
    """
    POST /core/tools/log/
    
    Registra um log de chamada de tool para auditoria.
    """
    try:
        body = json.loads(request.body)
        
        log_entry = ToolCallLog.objects.create(
            request_id=body.get("request_id", ""),
            tool=body.get("tool", ""),
            version=body.get("version", ""),
            client_key=body.get("client_key", ""),
            ok=body.get("ok", False),
            status_code=body.get("status_code"),
            latency_ms=body.get("latency_ms"),
            input_payload=body.get("input_payload"),
            output_payload=body.get("output_payload"),
            error_payload=body.get("error_payload")
        )
        
        return JsonResponse({"ok": True, "log_id": log_entry.id})
    
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Body inválido. Esperado JSON."},
            status=400
        )
    except Exception as e:
        logger.error(f"Erro ao registrar log: {e}")
        return JsonResponse(
            {"error": "Erro ao registrar log", "detail": str(e)},
            status=500
        )


"""
Serviço de Dispatcher para execução de tools MCP
Dispatcher unificado no Core Django que executa tools baseado no runtime configurado.
"""
import json
import time
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings
# PermissionError é built-in do Python, não precisa importar
from jsonschema import validate, ValidationError
from .models import Tool, ToolVersion, ToolCallLog, ClientApp
from .utils import resolve_prompt_info

logger = logging.getLogger(__name__)

# Configurações
OPENMIND_AI_URL = getattr(settings, 'OPENMIND_AI_URL', 'http://127.0.0.1:8001')
OPENMIND_AI_KEY = getattr(settings, 'OPENMIND_AI_KEY', None)
DDF_BASE_URL = getattr(settings, 'DDF_BASE_URL', 'http://ddf_service:8005')
DDF_TIMEOUT = getattr(settings, 'DDF_TIMEOUT', 60)
SPARKSCORE_BASE_URL = getattr(settings, 'SPARKSCORE_BASE_URL', 'http://sparkscore_service:8006')
SPARKSCORE_TIMEOUT = getattr(settings, 'SPARKSCORE_TIMEOUT', 30)
MCP_MAX_INPUT_BYTES = getattr(settings, 'MCP_MAX_INPUT_BYTES', 10485760)  # 10MB


def validate_input_size(input_data: Dict[str, Any]) -> None:
    """
    Valida o tamanho do input contra MCP_MAX_INPUT_BYTES.
    
    Raises:
        ValueError: Se o input exceder o limite
    """
    input_json = json.dumps(input_data, ensure_ascii=False)
    input_size = len(input_json.encode('utf-8'))
    
    if input_size > MCP_MAX_INPUT_BYTES:
        raise ValueError(
            f"Input size ({input_size} bytes) exceeds maximum allowed size "
            f"({MCP_MAX_INPUT_BYTES} bytes)"
        )
    
    logger.debug(f"Input size validated: {input_size} bytes")


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any], schema_name: str = "schema") -> None:
    """
    Valida dados contra um JSON Schema.
    
    Args:
        data: Dados a validar
        schema: Schema JSON Schema
        schema_name: Nome do schema para mensagens de erro
        
    Raises:
        ValueError: Se a validação falhar
    """
    if not schema:
        return  # Sem schema, não valida
    
    try:
        validate(instance=data, schema=schema)
        logger.debug(f"{schema_name} validation passed")
    except ValidationError as e:
        error_msg = f"{schema_name} validation failed: {e.message}"
        if e.path:
            error_msg += f" (path: {'/'.join(str(p) for p in e.path)})"
        raise ValueError(error_msg)


def truncate_payload(payload: Any, max_bytes: int = 10000) -> Any:
    """
    Trunca um payload para não exceder max_bytes quando serializado.
    
    Args:
        payload: Payload a truncar
        max_bytes: Tamanho máximo em bytes
        
    Returns:
        Payload truncado ou mensagem de truncamento
    """
    try:
        payload_json = json.dumps(payload, ensure_ascii=False)
        payload_size = len(payload_json.encode('utf-8'))
        
        if payload_size <= max_bytes:
            return payload
        
        # Truncar mantendo estrutura JSON válida
        truncated = json.dumps({
            "_truncated": True,
            "_original_size_bytes": payload_size,
            "_max_size_bytes": max_bytes,
            "_message": "Payload truncated for logging"
        })
        
        logger.warning(f"Payload truncated: {payload_size} bytes -> {len(truncated)} bytes")
        return json.loads(truncated)
    except Exception as e:
        logger.error(f"Error truncating payload: {e}")
        return {"_error": "Failed to truncate payload", "_exception": str(e)}


def execute_runtime_openmind_http(
    config: Dict[str, Any],
    input_data: Dict[str, Any],
    prompt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa runtime openmind_http.
    
    Config esperado:
    {
        "url": "http://openmind:8001/api/v1/analyze-product-image",
        "timeout_s": 60
    }
    
    Args:
        config: Configurações do runtime
        input_data: Dados de entrada (deve conter image_base64 ou image_url)
        prompt_text: Texto do prompt (resolvido do prompt_ref)
        
    Returns:
        dict: Resposta do OpenMind
        
    Raises:
        ValueError: Se input_data inválido
        requests.RequestException: Se erro na requisição
    """
    url = config.get("url", f"{OPENMIND_AI_URL}/api/v1/analyze-product-image")
    timeout = config.get("timeout_s", 60)
    
    # Extrair imagem do input_data
    image_base64 = input_data.get("image_base64")
    image_url = input_data.get("image_url")
    prompt_params = input_data.get("prompt_params", {})
    
    if not image_base64 and not image_url:
        raise ValueError("input_data deve conter 'image_base64' ou 'image_url'")
    
    # Preparar dados para multipart/form-data
    files = {}
    data = {}
    
    if image_base64:
        # Se for base64, decodificar e criar arquivo em memória
        import base64
        from io import BytesIO
        
        # Remover prefixo data:image se existir
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        
        try:
            image_bytes = base64.b64decode(image_base64)
            image_file = BytesIO(image_bytes)
            files['image'] = ('image.jpg', image_file, 'image/jpeg')
        except Exception as e:
            raise ValueError(f"Erro ao decodificar image_base64: {str(e)}")
    elif image_url:
        data['image_url'] = image_url
    
    # Adicionar prompt se disponível
    if prompt_text:
        data['prompt'] = prompt_text
        logger.info(f"Passando prompt para OpenMind ({len(prompt_text)} caracteres)")
    
    # Adicionar prompt_params se disponível
    if prompt_params:
        data['prompt_params'] = json.dumps(prompt_params)
    
    logger.info(f"Chamando OpenMind HTTP: {url}")
    
    headers = {}
    if OPENMIND_AI_KEY:
        headers['Authorization'] = f'Bearer {OPENMIND_AI_KEY}'
    
    try:
        response = requests.post(
            url,
            files=files if files else None,
            data=data,
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao chamar OpenMind: {e}")
        raise


def execute_runtime_prompt(
    config: Dict[str, Any],
    input_data: Dict[str, Any],
    prompt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa runtime prompt - envia prompt para LLM via OpenMind.
    
    Config esperado:
    {
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 2000,
        "url": "http://openmind:8001/chat/completions",
    }
    
    Args:
        config: Configurações do runtime
        input_data: Dados de entrada
        prompt_text: Texto do prompt (resolvido do prompt_ref)
        
    Returns:
        dict: Resposta do LLM
        
    Raises:
        ValueError: Se prompt_text não disponível
        requests.RequestException: Se erro na requisição
    """
    if not prompt_text:
        # Tentar buscar prompt inline do config
        prompt_text = config.get("prompt_inline")
        if not prompt_text:
            raise ValueError("Runtime 'prompt' requer prompt_text ou config.prompt_inline")
    
    # Configurações do LLM
    url = config.get("url", f"{OPENMIND_AI_URL}/chat/completions")
    model = config.get("model", "gpt-4o")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 2000)
    
    # Preparar mensagens para o chat
    if isinstance(input_data.get("messages"), list):
        messages = input_data["messages"]
    else:
        # Formatar prompt com input_data
        formatted_prompt = prompt_text
        if isinstance(input_data, dict):
            # Substituir {variavel} no prompt por valores do input
            for key, value in input_data.items():
                placeholder = f"{{{key}}}"
                if placeholder in formatted_prompt:
                    formatted_prompt = formatted_prompt.replace(placeholder, str(value))
        
        messages = [
            {"role": "system", "content": formatted_prompt},
            {"role": "user", "content": str(input_data) if not isinstance(input_data, str) else input_data}
        ]
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    logger.info(f"Executando runtime prompt: model={model}, prompt_length={len(prompt_text)}")
    
    headers = {}
    if OPENMIND_AI_KEY:
        headers["Authorization"] = f"Bearer {OPENMIND_AI_KEY}"
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        # Extrair conteúdo da resposta
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0].get("message", {}).get("content", "")
            return {
                "content": content,
                "model": result.get("model"),
                "usage": result.get("usage", {}),
                "raw_response": result
            }
        else:
            return result
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao executar runtime prompt: {e}")
        raise


def execute_runtime_ddf(
    config: Dict[str, Any],
    input_data: Dict[str, Any],
    prompt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa runtime ddf - delega execução para DDF Service.
    
    Config esperado:
    {
        "provider": "openai",  # opcional, sobrescreve detecção do DDF
        "timeout_s": 60
    }
    
    O DDF Service espera:
    {
        "text": str,  # Texto da tarefa
        "context": dict,  # Contexto adicional
        "provider": str,  # Opcional, sobrescreve detecção
        "params": dict  # Parâmetros adicionais
    }
    
    Args:
        config: Configurações do runtime
        input_data: Dados de entrada (pode conter "text" ou ser convertido)
        prompt_text: Texto do prompt (opcional, pode ser usado como "text")
        
    Returns:
        dict: Resposta do DDF Service (formato ExecuteResponse)
        
    Raises:
        requests.RequestException: Se erro na requisição
    """
    url = f"{DDF_BASE_URL}/ddf/execute"
    timeout = config.get("timeout_s", DDF_TIMEOUT)
    
    # Preparar payload para DDF
    # DDF espera "text" como campo principal
    text = input_data.get("text")
    if not text and prompt_text:
        # Se não tem "text" no input, usar prompt_text
        text = prompt_text
    elif not text:
        # Se não tem nenhum, tentar converter input_data para string
        text = json.dumps(input_data, ensure_ascii=False)
    
    # Context pode vir do input_data ou ser construído
    context = input_data.get("context", {})
    
    # Adicionar prompt ao context se disponível
    if prompt_text and "prompt" not in context:
        context["prompt"] = prompt_text
    
    # Provider override do config
    provider_override = config.get("provider")
    
    # Params adicionais (tudo que não é text/context)
    params = {k: v for k, v in input_data.items() if k not in ("text", "context")}
    
    payload = {
        "text": text,
        "context": context,
        "params": params
    }
    
    if provider_override:
        payload["provider"] = provider_override
    
    logger.info(f"Chamando DDF Service: {url} (text length: {len(text) if text else 0})")
    
    try:
        response = requests.post(
            url,
            json=payload,
            timeout=timeout
        )
        response.raise_for_status()
        result = response.json()
        
        # DDF retorna ExecuteResponse com estrutura:
        # {
        #   "success": bool,
        #   "request_id": str,
        #   "detection": dict,
        #   "delegation": dict,
        #   "result": dict,
        #   "execution_time": float
        # }
        # Retornar o "result" como output principal
        if result.get("success") and "result" in result:
            return result["result"]
        else:
            # Se não tem result, retornar resposta completa
            return result
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao chamar DDF Service: {e}")
        raise


def execute_runtime(
    runtime: str,
    config: Dict[str, Any],
    input_data: Dict[str, Any],
    prompt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa o runtime apropriado.
    
    Args:
        runtime: Tipo de runtime ("prompt", "openmind_http", "ddf", etc.)
        config: Configurações do runtime
        input_data: Dados de entrada
        prompt_text: Texto do prompt (resolvido do prompt_ref)
        
    Returns:
        dict: Resultado da execução
        
    Raises:
        ValueError: Se runtime desconhecido ou erro de validação
        requests.RequestException: Se erro na requisição HTTP
    """
    if runtime == "openmind_http":
        return execute_runtime_openmind_http(config, input_data, prompt_text=prompt_text)
    elif runtime == "prompt":
        return execute_runtime_prompt(config, input_data, prompt_text)
    elif runtime == "ddf":
        return execute_runtime_ddf(config, input_data, prompt_text=prompt_text)
    elif runtime == "sparkscore":
        return execute_runtime_sparkscore(config, input_data, prompt_text=prompt_text)
    elif runtime == "noop":
        return {"message": "No operation - tool not implemented"}
    elif runtime == "pipeline":
        return {"message": "Pipeline runtime - not implemented"}
    else:
        raise ValueError(f"Runtime desconhecido: {runtime}")


def execute_tool(
    tool_name: str,
    input_data: Dict[str, Any],
    client_key: Optional[str] = None,
    version: Optional[str] = None,
    context_pack: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None,
    trace_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa uma tool MCP (dispatcher unificado).
    
    Fluxo:
    1. Busca tool e versão
    2. Valida permissões do cliente
    3. Valida tamanho do input
    4. Resolve prompt_ref para prompt_text
    5. Valida input_schema
    6. Executa runtime
    7. Valida output_schema (não crítico)
    8. Registra log de execução
    9. Retorna resultado
    
    Args:
        tool_name: Nome da tool (ex: "vitrinezap.analisar_produto")
        input_data: Dados de entrada
        client_key: Chave do cliente (opcional, pode ser inferido via API key)
        version: Versão da tool (opcional, usa current se não fornecido)
        context_pack: Context Pack MCP-aware (opcional)
        request_id: UUID da requisição (gerado se None)
        trace_id: UUID do trace (gerado se None)
        
    Returns:
        dict: {
            "request_id": str,
            "trace_id": str,
            "tool": str,
            "version": str,
            "ok": bool,
            "output": dict | None,
            "error": dict | None,
            "latency_ms": int
        }
        
    Raises:
        Tool.DoesNotExist: Se tool não encontrada
        ToolVersion.DoesNotExist: Se versão não encontrada
        ValueError: Se validação falhar
        PermissionError: Se cliente não tem permissão
    """
    import uuid
    from datetime import datetime
    
    start_time = time.time()
    
    # Gerar IDs se ausentes
    if not request_id:
        request_id = str(uuid.uuid4())
    if not trace_id:
        trace_id = str(uuid.uuid4())
    
    logger.info(f"[{request_id}][{trace_id}] Executando tool: {tool_name} v{version or 'current'}")
    
    try:
        # 1. Buscar tool
        try:
            tool = Tool.objects.get(name=tool_name, is_active=True)
        except Tool.DoesNotExist:
            raise Tool.DoesNotExist(f"Tool '{tool_name}' não encontrada ou inativa")
        
        # 2. Buscar versão
        if version:
            try:
                tool_version = ToolVersion.objects.get(
                    tool=tool,
                    version=version,
                    is_active=True
                )
            except ToolVersion.DoesNotExist:
                raise ToolVersion.DoesNotExist(
                    f"Versão '{version}' não encontrada ou inativa para tool '{tool_name}'"
                )
        else:
            if not tool.current_version:
                raise ValueError(f"Tool '{tool_name}' não tem versão atual definida")
            tool_version = tool.current_version
        
        # 3. Validar permissões (se client_key fornecido)
        if client_key:
            try:
                client = ClientApp.objects.get(key=client_key, is_active=True)
            except ClientApp.DoesNotExist:
                raise PermissionError(f"ClientApp '{client_key}' não encontrado ou inativo")  # PermissionError é built-in do Python
            
            # Verificar se tool tem allowed_clients e se cliente está na lista
            if tool.allowed_clients.exists():
                if client not in tool.allowed_clients.all():
                    raise PermissionError(
                        f"Cliente '{client_key}' não tem permissão para usar tool '{tool_name}'"
                    )
        else:
            client_key = "unknown"
            client = None
        
        # 4. Validar tamanho do input
        validate_input_size(input_data)
        
        # 5. Resolver prompt_ref para prompt_text
        prompt_text = None
        prompt_info = None
        if tool_version.prompt_ref or (tool_version.config and tool_version.config.get("prompt_inline")):
            prompt_info = resolve_prompt_info(
                tool_version.prompt_ref,
                config=tool_version.config
            )
            if prompt_info and prompt_info.get('text'):
                prompt_text = prompt_info['text']
                logger.info(
                    f"[{request_id}][{trace_id}] Prompt resolvido: "
                    f"{prompt_info.get('nome', 'N/A')} (fonte: {prompt_info.get('fonte', 'desconhecida')})"
                )
        
        # 6. Validar input_schema
        if tool_version.input_schema:
            try:
                validate_json_schema(input_data, tool_version.input_schema, "input_schema")
                logger.debug(f"[{request_id}][{trace_id}] Input validado contra schema")
            except ValueError as e:
                raise ValueError(f"Input validation failed: {str(e)}")
        
        # 7. Executar runtime
        runtime = tool_version.runtime
        config = tool_version.config or {}
        
        logger.info(f"[{request_id}][{trace_id}] Executando runtime: {runtime}")
        
        try:
            output_data = execute_runtime(runtime, config, input_data, prompt_text=prompt_text)
            logger.info(f"[{request_id}][{trace_id}] Runtime executado com sucesso")
        except Exception as e:
            error_msg = str(e)
            logger.error(f"[{request_id}][{trace_id}] Erro ao executar runtime: {error_msg}", exc_info=True)
            
            # Calcular latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Registrar log de erro
            error_payload = {
                "code": "RUNTIME_EXECUTION_ERROR",
                "message": error_msg,
                "runtime": runtime,
                "exception_type": type(e).__name__
            }
            
            ToolCallLog.objects.create(
                request_id=request_id,
                trace_id=trace_id,
                tool=tool_name,
                version=tool_version.version,
                client_key=client_key,
                ok=False,
                status_code=500,
                latency_ms=latency_ms,
                input_payload=truncate_payload(input_data),
                error_payload=error_payload
            )
            
            return {
                "request_id": request_id,
                "trace_id": trace_id,
                "tool": tool_name,
                "version": tool_version.version,
                "ok": False,
                "error": error_payload,
                "latency_ms": latency_ms
            }
        
        # 8. Validar output_schema (não crítico)
        if tool_version.output_schema and output_data:
            try:
                validate_json_schema(output_data, tool_version.output_schema, "output_schema")
                logger.debug(f"[{request_id}][{trace_id}] Output validado contra schema")
            except ValueError as e:
                logger.warning(f"[{request_id}][{trace_id}] Output validation failed (não crítico): {e}")
        
        # 9. Calcular latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 10. Registrar log de sucesso
        ToolCallLog.objects.create(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name,
            version=tool_version.version,
            client_key=client_key,
            ok=True,
            status_code=200,
            latency_ms=latency_ms,
            input_payload=truncate_payload(input_data),
            output_payload=truncate_payload(output_data)
        )
        
        # 11. Retornar resultado
        return {
            "request_id": request_id,
            "trace_id": trace_id,
            "tool": tool_name,
            "version": tool_version.version,
            "ok": True,
            "output": output_data,
            "latency_ms": latency_ms
        }
        
    except (Tool.DoesNotExist, ToolVersion.DoesNotExist, ValueError, PermissionError) as e:
        # Erros de validação/permissão
        latency_ms = int((time.time() - start_time) * 1000)
        error_payload = {
            "code": type(e).__name__,
            "message": str(e)
        }
        
        ToolCallLog.objects.create(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name,
            version=version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=400 if isinstance(e, ValueError) else (403 if isinstance(e, PermissionError) else 404),
            latency_ms=latency_ms,
            input_payload=truncate_payload(input_data),
            error_payload=error_payload
        )
        
        raise
    except Exception as e:
        # Erros inesperados
        latency_ms = int((time.time() - start_time) * 1000)
        error_payload = {
            "code": "INTERNAL_ERROR",
            "message": str(e),
            "exception_type": type(e).__name__
        }
        
        logger.error(f"[{request_id}][{trace_id}] Erro inesperado: {e}", exc_info=True)
        
        ToolCallLog.objects.create(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name,
            version=version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=500,
            latency_ms=latency_ms,
            input_payload=truncate_payload(input_data),
            error_payload=error_payload
        )
        
        raise


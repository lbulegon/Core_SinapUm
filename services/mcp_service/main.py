"""
MCP Service - Model Context Protocol Service
Serviço FastAPI que atua como gateway para tools versionadas.

O MCP Service consulta o Core Registry (Django) para resolver tools
e executa chamadas seguindo o protocolo MCP.
"""
import os
import uuid
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import requests
import jsonschema
from jsonschema import validate, ValidationError

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração
SINAPUM_CORE_URL = os.getenv("SINAPUM_CORE_URL", "http://web:5000")
OPENMIND_SERVICE_URL = os.getenv("OPENMIND_SERVICE_URL", "http://openmind:8001")
BASE_PATH = "/mcp"

# Inicializar FastAPI
app = FastAPI(
    title="MCP Service - SinapUm",
    description="Model Context Protocol Service - Gateway para tools versionadas",
    version="1.0.0"
)

# ============================================================================
# Modelos Pydantic - Context Pack (MCP-Aware)
# ============================================================================

class ContextPackMeta(BaseModel):
    """Metadados do Context Pack"""
    request_id: Optional[str] = Field(None, description="UUID da requisição (gerado se ausente)")
    trace_id: Optional[str] = Field(None, description="UUID do trace (gerado se ausente)")
    timestamp: Optional[str] = Field(None, description="ISO8601 timestamp (gerado se ausente)")
    actor: Optional[Dict[str, Any]] = Field(None, description="Actor: {type: 'user|system|service', id: 'string'}")
    source: Optional[Dict[str, Any]] = Field(None, description="Source: {channel: 'web|whatsapp|api|admin', conversation_id: 'string'}")

class ContextPackTask(BaseModel):
    """Task do Context Pack"""
    name: Optional[str] = None
    goal: Optional[str] = None
    constraints: Optional[List[str]] = None

class ContextPackContext(BaseModel):
    """Context do Context Pack"""
    history_ref: Optional[Dict[str, Any]] = Field(None, description="History ref: {store: 'postgres', thread_id: 'string', summary_id: 'string'}")
    user_profile: Optional[Dict[str, Any]] = None
    domain_profile: Optional[Dict[str, Any]] = None

class ContextPackState(BaseModel):
    """State do Context Pack"""
    state_ref: Optional[Dict[str, Any]] = Field(None, description="State ref: {store: 'redis|postgres', key: 'string', ttl_sec: 3600}")
    snapshot: Optional[Dict[str, Any]] = None

class ContextPackIntent(BaseModel):
    """Intent do Context Pack"""
    current: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    candidates: Optional[List[Dict[str, Any]]] = None

class ContextPackResponseContract(BaseModel):
    """Response Contract do Context Pack"""
    mode: Optional[str] = Field(None, description="tool_call|message|json")
    language: Optional[str] = Field(None, description="pt-BR, en-US, etc")

class ContextPack(BaseModel):
    """Context Pack completo (MCP-Aware)"""
    meta: Optional[ContextPackMeta] = None
    task: Optional[ContextPackTask] = None
    context: Optional[ContextPackContext] = None
    state: Optional[ContextPackState] = None
    intent: Optional[ContextPackIntent] = None
    policies: Optional[List[str]] = None
    response_contract: Optional[ContextPackResponseContract] = None

# ============================================================================
# Modelos Pydantic - Request/Response
# ============================================================================

class ToolCallRequest(BaseModel):
    """Request para chamada de tool (compatível com formato legado e MCP-aware)"""
    tool: str = Field(..., description="Nome da tool (ex: vitrinezap.analisar_produto)")
    version: Optional[str] = Field(None, description="Versão da tool (opcional, usa current se não fornecido)")
    context_pack: Optional[ContextPack] = Field(None, description="Context Pack MCP-aware (opcional)")
    input: Dict[str, Any] = Field(..., description="Input da tool")

class ErrorDetail(BaseModel):
    """Detalhes estruturados de erro"""
    code: str = Field(..., description="Código do erro")
    message: str = Field(..., description="Mensagem do erro")
    details: Optional[Dict[str, Any]] = Field(None, description="Detalhes adicionais")

class ToolCallResponse(BaseModel):
    """Response de chamada de tool (padronizado)"""
    request_id: str
    trace_id: Optional[str] = None
    tool: str
    version: str
    ok: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetail] = None
    latency_ms: int

# ============================================================================
# Helpers
# ============================================================================

def generate_minimal_context_pack(request_id: Optional[str] = None, trace_id: Optional[str] = None) -> ContextPack:
    """
    Gera um Context Pack mínimo quando não fornecido na requisição.
    
    Args:
        request_id: UUID da requisição (gerado se None)
        trace_id: UUID do trace (gerado se None)
    
    Returns:
        ContextPack com valores padrão
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    if trace_id is None:
        trace_id = str(uuid.uuid4())
    
    return ContextPack(
        meta=ContextPackMeta(
            request_id=request_id,
            trace_id=trace_id,
            timestamp=datetime.utcnow().isoformat() + "Z",
            actor={"type": "service", "id": "mcp_service"},
            source={"channel": "api", "conversation_id": None}
        ),
        task=None,
        context=None,
        state=None,
        intent=None,
        policies=None,
        response_contract=ContextPackResponseContract(mode="json", language="pt-BR")
    )

def normalize_context_pack(context_pack: Optional[ContextPack], request_id: Optional[str] = None, trace_id: Optional[str] = None) -> ContextPack:
    """
    Normaliza um Context Pack, garantindo request_id e trace_id.
    
    Args:
        context_pack: Context Pack fornecido (pode ser None)
        request_id: UUID da requisição (gerado se None)
        trace_id: UUID do trace (gerado se None)
    
    Returns:
        ContextPack normalizado com request_id e trace_id garantidos
    """
    if context_pack is None:
        return generate_minimal_context_pack(request_id, trace_id)
    
    # Garantir que meta existe
    if context_pack.meta is None:
        context_pack.meta = ContextPackMeta()
    
    # Garantir request_id e trace_id
    if not context_pack.meta.request_id:
        context_pack.meta.request_id = request_id or str(uuid.uuid4())
    if not context_pack.meta.trace_id:
        context_pack.meta.trace_id = trace_id or str(uuid.uuid4())
    if not context_pack.meta.timestamp:
        context_pack.meta.timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Valores padrão para meta se ausentes
    if not context_pack.meta.actor:
        context_pack.meta.actor = {"type": "service", "id": "mcp_service"}
    if not context_pack.meta.source:
        context_pack.meta.source = {"channel": "api", "conversation_id": None}
    
    return context_pack

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Valida dados contra um JSON Schema.
    Raises ValidationError se inválido.
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")

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
        prompt_text: Texto do prompt (resolvido do prompt_ref) - será passado para o OpenMind
    """
    url = config.get("url", f"{OPENMIND_SERVICE_URL}/api/v1/analyze-product-image")
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
        # Se for URL, passar como parâmetro
        data['image_url'] = image_url
    
    # Adicionar prompt se disponível
    if prompt_text:
        data['prompt'] = prompt_text
        logger.info(f"Passando prompt para OpenMind ({len(prompt_text)} caracteres)")
    
    # Adicionar prompt_params se disponível
    if prompt_params:
        import json
        data['prompt_params'] = json.dumps(prompt_params)
    
    logger.info(f"Chamando OpenMind HTTP: {url}")
    if prompt_text:
        logger.info(f"Prompt incluído: {len(prompt_text)} caracteres")
    
    try:
        response = requests.post(
            url,
            files=files if files else None,
            data=data,
            timeout=timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao chamar OpenMind: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"OpenMind service error: {str(e)}"
        )

def execute_runtime_prompt(
    config: Dict[str, Any],
    input_data: Dict[str, Any],
    prompt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa runtime prompt - envia prompt para LLM via OpenMind.
    
    Config esperado:
    {
        "model": "gpt-4o",  # opcional, usa padrão do OpenMind
        "temperature": 0.7,  # opcional
        "max_tokens": 2000,  # opcional
        "url": "http://openmind:8001/chat/completions",  # opcional
    }
    
    O prompt_text vem do execution_plan (resolvido do prompt_ref).
    Se não vier, tenta buscar de config.get("prompt_inline").
    """
    if not prompt_text:
        # Tentar buscar prompt inline do config
        prompt_text = config.get("prompt_inline")
        if not prompt_text:
            raise ValueError("Runtime 'prompt' requer prompt_text ou config.prompt_inline")
    
    # Configurações do LLM
    url = config.get("url", f"{OPENMIND_SERVICE_URL}/chat/completions")
    model = config.get("model", "gpt-4o")
    temperature = config.get("temperature", 0.7)
    max_tokens = config.get("max_tokens", 2000)
    
    # Preparar mensagens para o chat
    # Se input_data tiver "messages", usar diretamente
    # Senão, criar mensagem com prompt + input formatado
    if isinstance(input_data.get("messages"), list):
        messages = input_data["messages"]
    else:
        # Formatar prompt com input_data
        # Substituir variáveis no prompt se necessário
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
    
    try:
        # Usar API key do OpenMind se disponível
        headers = {}
        openmind_key = os.getenv("OPENMIND_AI_KEY", "")
        if openmind_key:
            headers["Authorization"] = f"Bearer {openmind_key}"
        
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
                "raw_response": result  # Incluir resposta completa para debug
            }
        else:
            return result
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao executar runtime prompt: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"LLM service error: {str(e)}"
        )


def execute_runtime(
    runtime: str,
    config: Dict[str, Any],
    input_data: Dict[str, Any],
    prompt_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executa o runtime apropriado.
    
    Args:
        runtime: Tipo de runtime ("prompt", "openmind_http", etc.)
        config: Configurações do runtime
        input_data: Dados de entrada
        prompt_text: Texto do prompt (resolvido do prompt_ref) - usado para runtime "prompt"
    """
    if runtime == "openmind_http":
        return execute_runtime_openmind_http(config, input_data, prompt_text=prompt_text)
    elif runtime == "prompt":
        return execute_runtime_prompt(config, input_data, prompt_text)
    elif runtime == "noop":
        return {"message": "No operation - tool not implemented"}
    elif runtime == "pipeline":
        return {"message": "Pipeline runtime - not implemented"}
    elif runtime == "ddf":
        return {"message": "DDF runtime - not implemented"}
    else:
        raise ValueError(f"Runtime desconhecido: {runtime}")

def log_tool_call(
    request_id: str,
    trace_id: Optional[str],
    tool: str,
    version: str,
    client_key: str,
    ok: bool,
    status_code: int,
    latency_ms: int,
    input_payload: Optional[Dict[str, Any]] = None,
    output_payload: Optional[Dict[str, Any]] = None,
    error_payload: Optional[Any] = None,
    context_pack: Optional[ContextPack] = None
):
    """
    Registra log de chamada no Core Registry.
    
    Args:
        request_id: UUID da requisição
        trace_id: UUID do trace (opcional, será incluído no payload)
        tool: Nome da tool
        version: Versão da tool
        client_key: Chave do cliente
        ok: Sucesso/falha
        status_code: Código HTTP
        latency_ms: Latência em milissegundos
        input_payload: Payload de entrada
        output_payload: Payload de saída
        error_payload: Payload de erro (pode ser string ou dict)
        context_pack: Context Pack completo (opcional)
    """
    try:
        # Enriquecer input_payload com context_pack se disponível
        enriched_input = input_payload.copy() if input_payload else {}
        if context_pack:
            enriched_input["_context_pack"] = context_pack.dict(exclude_none=True)
        
        log_payload = {
            "request_id": request_id,
            "trace_id": trace_id,  # Novo campo
            "tool": tool,
            "version": version,
            "client_key": client_key,
            "ok": ok,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "input_payload": enriched_input,
            "output_payload": output_payload,
            "error_payload": error_payload
        }
        
        requests.post(
            f"{SINAPUM_CORE_URL}/core/tools/log/",
            json=log_payload,
            timeout=2
        )
    except Exception as e:
        logger.warning(f"Erro ao registrar log (não crítico): {e}")

# ============================================================================
# Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """
    Health check do MCP Service
    """
    try:
        # Verificar se o Core está acessível
        core_health = requests.get(
            f"{SINAPUM_CORE_URL}/health",
            timeout=2
        )
        core_status = "healthy" if core_health.status_code == 200 else "unhealthy"
    except Exception as e:
        logger.warning(f"Core não acessível: {e}")
        core_status = "unreachable"
    
    return {
        "status": "healthy",
        "service": "mcp_service",
        "core_status": core_status,
        "core_url": SINAPUM_CORE_URL
    }

@app.get(f"{BASE_PATH}/tools")
async def list_tools():
    """
    Lista todas as tools disponíveis.
    Consulta o Core Registry (Django) e repassa a resposta.
    """
    try:
        logger.info(f"Consultando tools no Core: {SINAPUM_CORE_URL}/core/tools")
        
        response = requests.get(
            f"{SINAPUM_CORE_URL}/core/tools",
            timeout=5
        )
        response.raise_for_status()
        
        tools = response.json()
        logger.info(f"Retornando {len(tools)} tools")
        
        return JSONResponse(content=tools)
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro ao consultar Core: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Core Registry não disponível: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno: {str(e)}"
        )

@app.post(f"{BASE_PATH}/call")
async def call_tool(
    request: ToolCallRequest,
    x_sinapum_key: Optional[str] = Header(None, alias="X-SINAPUM-KEY")
):
    """
    Chama uma tool específica (MCP-aware).
    
    Suporta dois formatos:
    1. Formato legado: {tool, version?, input}
    2. Formato MCP-aware: {tool, version?, context_pack?, input}
    
    Fluxo completo:
    1. Normaliza context_pack (gera request_id/trace_id se ausentes)
    2. Autentica client (API key)
    3. Chama Django /core/tools/resolve (opcionalmente envia context_pack)
    4. Valida input_schema
    5. Executa runtime
    6. Valida output_schema
    7. Grava log no Django (com trace_id e context_pack)
    8. Responde no formato MCP padrão (com erro estruturado se falhar)
    """
    start_time = time.time()
    client_key = None
    tool_name = None
    tool_version = None
    status_code = 200
    error_detail: Optional[ErrorDetail] = None
    output_data = None
    
    # 1. Normalizar context_pack (garantir request_id e trace_id)
    context_pack = normalize_context_pack(request.context_pack)
    request_id = context_pack.meta.request_id
    trace_id = context_pack.meta.trace_id
    
    logger.info(f"[{request_id}][{trace_id}] Chamando tool: {request.tool} v{request.version or 'current'}")
    
    try:
        # 2. Consultar Core Registry para resolver a tool
        resolve_payload = {
            "tool": request.tool,
            "input": request.input
        }
        
        if request.version:
            resolve_payload["version"] = request.version
        
        # Opcionalmente enviar context_pack ao Core Registry (se aceitar)
        # Por enquanto, mantemos compatibilidade: Core Registry não precisa aceitar ainda
        # Mas podemos incluir em um campo opcional para futuro
        if context_pack:
            resolve_payload["_context_pack"] = context_pack.dict(exclude_none=True)
        
        headers = {}
        if x_sinapum_key:
            headers["X-SINAPUM-KEY"] = x_sinapum_key
        
        logger.info(f"[{request_id}][{trace_id}] Resolvendo tool no Core: {SINAPUM_CORE_URL}/core/tools/resolve")
        
        resolve_response = requests.post(
            f"{SINAPUM_CORE_URL}/core/tools/resolve",
            json=resolve_payload,
            headers=headers,
            timeout=10
        )
        resolve_response.raise_for_status()
        
        execution_plan = resolve_response.json()
        client_key = execution_plan.get("client_key", "unknown")
        tool_name = execution_plan.get("tool", request.tool)
        tool_version = execution_plan.get("version", request.version or "unknown")
        runtime = execution_plan.get("runtime")
        config = execution_plan.get("config", {})
        input_schema = execution_plan.get("input_schema", {})
        output_schema = execution_plan.get("output_schema", {})
        prompt_text = execution_plan.get("prompt_text")  # Prompt resolvido do prompt_ref
        prompt_info = execution_plan.get("prompt_info")  # Informações completas do prompt
        
        logger.info(f"[{request_id}][{trace_id}] Tool resolvida: {tool_name}@{tool_version} runtime={runtime}")
        if prompt_text:
            logger.info(f"[{request_id}][{trace_id}] Prompt disponível: {len(prompt_text)} caracteres")
        
        # 3. Validar input_schema
        if input_schema:
            try:
                validate_json_schema(request.input, input_schema)
                logger.info(f"[{request_id}][{trace_id}] Input validado contra schema")
            except ValueError as e:
                error_detail = ErrorDetail(
                    code="INPUT_VALIDATION_FAILED",
                    message=f"Input validation failed: {str(e)}",
                    details={"schema": input_schema, "input": request.input}
                )
                status_code = 400
                raise ValueError(str(e))
        
        # 4. Executar runtime (passa prompt_text para runtime "prompt")
        if runtime:
            logger.info(f"[{request_id}][{trace_id}] Executando runtime: {runtime}")
            try:
                output_data = execute_runtime(runtime, config, request.input, prompt_text=prompt_text)
                logger.info(f"[{request_id}][{trace_id}] Runtime executado com sucesso")
                
                # Adicionar informações do prompt no cadastro_meta se o output tiver essa estrutura
                if isinstance(output_data, dict) and output_data.get('data') and isinstance(output_data['data'], dict):
                    if 'cadastro_meta' in output_data['data']:
                        if prompt_info:
                            output_data['data']['cadastro_meta']['prompt_usado'] = {
                                'nome': prompt_info.get('nome', 'Desconhecido'),
                                'versao': prompt_info.get('versao', 'N/A'),
                                'fonte': prompt_info.get('fonte', 'Não informado'),
                                'sistema': prompt_info.get('sistema'),
                                'tipo_prompt': prompt_info.get('tipo_prompt', 'analise_imagem_produto'),
                                'parametros': prompt_info.get('parametros', {}),
                                'prompt_ref': prompt_info.get('prompt_ref')
                            }
                        else:
                            output_data['data']['cadastro_meta']['prompt_usado'] = {
                                'nome': 'Desconhecido',
                                'versao': 'N/A',
                                'fonte': 'Não informado',
                                'sistema': None,
                                'tipo_prompt': 'analise_imagem_produto',
                                'parametros': {},
                                'prompt_ref': execution_plan.get('prompt_ref')
                            }
            except Exception as e:
                error_detail = ErrorDetail(
                    code="RUNTIME_EXECUTION_ERROR",
                    message=f"Runtime '{runtime}' execution failed: {str(e)}",
                    details={"runtime": runtime, "config": config}
                )
                status_code = 500
                raise
        else:
            output_data = {"message": "No runtime specified"}
        
        # 5. Validar output_schema
        if output_schema and output_data:
            try:
                validate_json_schema(output_data, output_schema)
                logger.info(f"[{request_id}][{trace_id}] Output validado contra schema")
            except ValueError as e:
                logger.warning(f"[{request_id}][{trace_id}] Output validation failed (não crítico): {e}")
                # Não falhamos aqui, apenas logamos
        
        # 6. Calcular latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 7. Registrar log (assíncrono, não bloqueia)
        log_tool_call(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name,
            version=tool_version,
            client_key=client_key,
            ok=True,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            output_payload=output_data,
            context_pack=context_pack
        )
        
        # 8. Retornar resposta
        return ToolCallResponse(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name,
            version=tool_version,
            ok=True,
            output=output_data,
            latency_ms=latency_ms
        )
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        error_detail = ErrorDetail(
            code="CORE_REGISTRY_ERROR",
            message=f"Core Registry error: {str(e)}",
            details={
                "status_code": e.response.status_code if e.response else None,
                "response": e.response.text if e.response else None
            }
        )
        logger.error(f"[{request_id}][{trace_id}] {error_detail.message}")
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Registrar log de erro
        log_tool_call(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name or request.tool,
            version=tool_version or request.version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            error_payload=error_detail.dict(),
            context_pack=context_pack
        )
        
        # Retornar resposta de erro estruturada
        return JSONResponse(
            status_code=status_code,
            content=ToolCallResponse(
                request_id=request_id,
                trace_id=trace_id,
                tool=tool_name or request.tool,
                version=tool_version or request.version or "unknown",
                ok=False,
                error=error_detail,
                latency_ms=latency_ms
            ).dict()
        )
    
    except ValueError as e:
        status_code = 400
        if not error_detail:
            error_detail = ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(e),
                details={}
            )
        logger.error(f"[{request_id}][{trace_id}] {error_detail.message}")
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Registrar log de erro
        log_tool_call(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name or request.tool,
            version=tool_version or request.version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            error_payload=error_detail.dict(),
            context_pack=context_pack
        )
        
        # Retornar resposta de erro estruturada
        return JSONResponse(
            status_code=status_code,
            content=ToolCallResponse(
                request_id=request_id,
                trace_id=trace_id,
                tool=tool_name or request.tool,
                version=tool_version or request.version or "unknown",
                ok=False,
                error=error_detail,
                latency_ms=latency_ms
            ).dict()
        )
    
    except Exception as e:
        status_code = 500
        error_detail = ErrorDetail(
            code="INTERNAL_ERROR",
            message=f"Internal error: {str(e)}",
            details={"exception_type": type(e).__name__}
        )
        logger.error(f"[{request_id}][{trace_id}] {error_detail.message}", exc_info=True)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Registrar log de erro
        log_tool_call(
            request_id=request_id,
            trace_id=trace_id,
            tool=tool_name or request.tool,
            version=tool_version or request.version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            error_payload=error_detail.dict(),
            context_pack=context_pack
        )
        
        # Retornar resposta de erro estruturada
        return JSONResponse(
            status_code=status_code,
            content=ToolCallResponse(
                request_id=request_id,
                trace_id=trace_id,
                tool=tool_name or request.tool,
                version=tool_version or request.version or "unknown",
                ok=False,
                error=error_detail,
                latency_ms=latency_ms
            ).dict()
        )

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7010,
        reload=False,
        log_level="info"
    )

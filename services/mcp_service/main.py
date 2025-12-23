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
from typing import Dict, Any, Optional
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
# Modelos Pydantic
# ============================================================================

class ToolCallRequest(BaseModel):
    """Request para chamada de tool"""
    tool: str = Field(..., description="Nome da tool (ex: vitrinezap.analisar_produto)")
    version: Optional[str] = Field(None, description="Versão da tool (opcional, usa current se não fornecido)")
    input: Dict[str, Any] = Field(..., description="Input da tool")

class ToolCallResponse(BaseModel):
    """Response de chamada de tool"""
    request_id: str
    tool: str
    version: str
    ok: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: int

# ============================================================================
# Helpers
# ============================================================================

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """
    Valida dados contra um JSON Schema.
    Raises ValidationError se inválido.
    """
    try:
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValueError(f"Schema validation failed: {e.message}")

def execute_runtime_openmind_http(config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa runtime openmind_http.
    
    Config esperado:
    {
        "url": "http://openmind:8001/agent/run",
        "agent": "vitrinezap_product_analyst",
        "timeout_s": 45
    }
    """
    url = config.get("url", f"{OPENMIND_SERVICE_URL}/agent/run")
    agent = config.get("agent", "default")
    timeout = config.get("timeout_s", 45)
    
    payload = {
        "agent": agent,
        "input": input_data
    }
    
    logger.info(f"Chamando OpenMind HTTP: {url} com agent={agent}")
    
    try:
        response = requests.post(
            url,
            json=payload,
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
        return execute_runtime_openmind_http(config, input_data)
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
    tool: str,
    version: str,
    client_key: str,
    ok: bool,
    status_code: int,
    latency_ms: int,
    input_payload: Optional[Dict[str, Any]] = None,
    output_payload: Optional[Dict[str, Any]] = None,
    error_payload: Optional[str] = None
):
    """
    Registra log de chamada no Core Registry.
    """
    try:
        log_payload = {
            "request_id": request_id,
            "tool": tool,
            "version": version,
            "client_key": client_key,
            "ok": ok,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "input_payload": input_payload,
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
    Chama uma tool específica.
    
    Fluxo completo:
    1. Autentica client (API key)
    2. Chama Django /core/tools/resolve
    3. Valida input_schema
    4. Executa runtime
    5. Valida output_schema
    6. Grava log no Django
    7. Responde no formato MCP padrão
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()
    client_key = None
    tool_name = None
    tool_version = None
    status_code = 200
    error_message = None
    output_data = None
    
    try:
        logger.info(f"[{request_id}] Chamando tool: {request.tool} v{request.version or 'current'}")
        
        # 1. Consultar Core Registry para resolver a tool
        resolve_payload = {
            "tool": request.tool,
            "input": request.input
        }
        
        if request.version:
            resolve_payload["version"] = request.version
        
        headers = {}
        if x_sinapum_key:
            headers["X-SINAPUM-KEY"] = x_sinapum_key
        
        logger.info(f"[{request_id}] Resolvendo tool no Core: {SINAPUM_CORE_URL}/core/tools/resolve")
        
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
        
        logger.info(f"[{request_id}] Tool resolvida: {tool_name}@{tool_version} runtime={runtime}")
        if prompt_text:
            logger.info(f"[{request_id}] Prompt disponível: {len(prompt_text)} caracteres")
        
        # 2. Validar input_schema
        if input_schema:
            try:
                validate_json_schema(request.input, input_schema)
                logger.info(f"[{request_id}] Input validado contra schema")
            except ValueError as e:
                error_message = f"Input validation failed: {str(e)}"
                status_code = 400
                raise ValueError(error_message)
        
        # 3. Executar runtime (passa prompt_text para runtime "prompt")
        if runtime:
            logger.info(f"[{request_id}] Executando runtime: {runtime}")
            output_data = execute_runtime(runtime, config, request.input, prompt_text=prompt_text)
            logger.info(f"[{request_id}] Runtime executado com sucesso")
        else:
            output_data = {"message": "No runtime specified"}
        
        # 4. Validar output_schema
        if output_schema and output_data:
            try:
                validate_json_schema(output_data, output_schema)
                logger.info(f"[{request_id}] Output validado contra schema")
            except ValueError as e:
                logger.warning(f"[{request_id}] Output validation failed (não crítico): {e}")
                # Não falhamos aqui, apenas logamos
        
        # 5. Calcular latency
        latency_ms = int((time.time() - start_time) * 1000)
        
        # 6. Registrar log (assíncrono, não bloqueia)
        log_tool_call(
            request_id=request_id,
            tool=tool_name,
            version=tool_version,
            client_key=client_key,
            ok=True,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            output_payload=output_data
        )
        
        # 7. Retornar resposta
        return ToolCallResponse(
            request_id=request_id,
            tool=tool_name,
            version=tool_version,
            ok=True,
            output=output_data,
            latency_ms=latency_ms
        )
    
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response else 500
        error_message = f"Core Registry error: {str(e)}"
        logger.error(f"[{request_id}] {error_message}")
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Registrar log de erro
        log_tool_call(
            request_id=request_id,
            tool=tool_name or request.tool,
            version=tool_version or request.version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            error_payload=error_message
        )
        
        raise HTTPException(status_code=status_code, detail=error_message)
    
    except ValueError as e:
        status_code = 400
        error_message = str(e)
        logger.error(f"[{request_id}] {error_message}")
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Registrar log de erro
        log_tool_call(
            request_id=request_id,
            tool=tool_name or request.tool,
            version=tool_version or request.version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            error_payload=error_message
        )
        
        raise HTTPException(status_code=status_code, detail=error_message)
    
    except Exception as e:
        status_code = 500
        error_message = f"Internal error: {str(e)}"
        logger.error(f"[{request_id}] {error_message}", exc_info=True)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Registrar log de erro
        log_tool_call(
            request_id=request_id,
            tool=tool_name or request.tool,
            version=tool_version or request.version or "unknown",
            client_key=client_key or "unknown",
            ok=False,
            status_code=status_code,
            latency_ms=latency_ms,
            input_payload=request.input,
            error_payload=error_message
        )
        
        raise HTTPException(status_code=status_code, detail=error_message)

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

"""
Serviço de Dispatcher para execução de tools MCP
Dispatcher unificado no Core Django que executa tools baseado no runtime configurado.
"""
import json
import time
import logging
import requests
from typing import Any, Dict, List, Optional
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


def _execute_tool_core_openmind_process_inbound(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.openmind_process_inbound` — evento canónico + contexto → serviço OpenMind
    (POST /api/v1/process-message). Substitui chamada HTTP directa a partir do app_ai_bridge.
    """
    event = input_data.get("event")
    context = input_data.get("context")
    if not event or not isinstance(event, dict):
        raise ValueError("core.openmind_process_inbound: 'event' (object) é obrigatório")
    if context is None:
        context = {}
    if not isinstance(context, dict):
        raise ValueError("core.openmind_process_inbound: 'context' deve ser object")

    base = str(
        getattr(settings, "OPENMIND_BASE_URL", "http://127.0.0.1:8001") or "http://127.0.0.1:8001"
    ).rstrip("/")
    url = f"{base}/api/v1/process-message"
    # O serviço OpenMind (FastAPI) valida o Bearer contra OPENMIND_AI_API_KEY; no Core costuma
    # coincidir com OPENMIND_AI_KEY. OPENMIND_TOKEN é o alias usado no bridge.
    token = str(
        getattr(settings, "OPENMIND_TOKEN", None)
        or getattr(settings, "OPENMIND_AI_KEY", None)
        or ""
    ).strip()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    timeout = int(getattr(settings, "OPENMIND_TIMEOUT", 30) or 30)
    from .openmind_process_message import (
        build_process_message_request,
        map_process_message_response_to_bridge,
    )

    try:
        payload = build_process_message_request(event, context)
    except ValueError as e:
        logger.error("core.openmind_process_inbound: payload inválido: %s", e)
        raise

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logger.error("core.openmind_process_inbound: erro HTTP OpenMind: %s", e)
        raise ValueError(f"OpenMind indisponível: {e}") from e
    if not isinstance(data, dict):
        raise ValueError("Resposta OpenMind inválida (não-JSON object)")

    return map_process_message_response_to_bridge(data)


def _execute_tool_core_openmind_analyze_product_image(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.openmind_analyze_product_image` — POST analyze-product-image (openmind_http).
    Input: image_base64 e/ou image_url; opcional prompt, prompt_params, timeout_s.
    """
    url_base = str(
        getattr(settings, "OPENMIND_IMAGE_URL", None)
        or getattr(settings, "OPENMIND_AI_URL", None)
        or "http://127.0.0.1:8001"
    ).rstrip("/")
    config = {
        "url": f"{url_base}/api/v1/analyze-product-image",
        "timeout_s": int(input_data.get("timeout_s", 60) or 60),
    }
    prompt_text = (input_data.get("prompt") or "").strip() or None
    return execute_runtime_openmind_http(config, input_data, prompt_text=prompt_text)


def _execute_tool_core_openmind_chat_completions(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.openmind_chat_completions` — POST /chat/completions no serviço OpenMind.
    Input: `messages` (lista OpenAI) ou corpo mínimo; model/temperature/max_tokens opcionais.
    """
    base = str(
        getattr(settings, "OPENMIND_AI_URL", None) or getattr(settings, "OPENMIND_BASE_URL", "http://127.0.0.1:8001")
    ).rstrip("/")
    config: Dict[str, Any] = {
        "url": f"{base}/chat/completions",
        "model": input_data.get("model") or getattr(settings, "OPENMIND_ORG_MODEL", "gpt-4o"),
        "temperature": float(input_data.get("temperature", 0.4)),
        "max_tokens": int(input_data.get("max_tokens", 1024)),
    }
    return execute_runtime_prompt(config, input_data, prompt_text=None)


def _execute_tool_core_rag_query(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tool MCP `core.rag_query` — retrieval no vectorstore_service."""
    from core.services.vectorstore_client import vectorstore_search

    q = (input_data.get("query") or input_data.get("text") or "").strip()
    k = int(input_data.get("k", 5) or 5)
    include_text = input_data.get("include_text", True)
    if isinstance(include_text, str):
        include_text = include_text.lower() in ("1", "true", "yes", "on")
    id_prefix = (input_data.get("id_prefix") or input_data.get("prefix") or "").strip()
    results = vectorstore_search(q, k=k, include_text=bool(include_text))
    if id_prefix:
        results = [r for r in results if str(r.get("id", "")).startswith(id_prefix)]
    return {"results": results, "query": q, "k": k, "id_prefix": id_prefix or None}


def _execute_tool_core_rag_ingest(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tool MCP `core.rag_ingest` — upsert de chunks de texto no vectorstore (ex.: gastronomia)."""
    from core.services.ingestion.pdf_ingestor import (
        DEFAULT_CHUNK_WORDS,
        ID_PREFIX,
        ingest_chunk_strings,
        ingest_text_as_chunks,
    )

    domain = str(input_data.get("domain") or "gastronomia").strip() or "gastronomia"
    id_prefix = str(input_data.get("id_prefix") or ID_PREFIX).strip() or ID_PREFIX
    source = str(input_data.get("source") or "mcp").strip() or "mcp"
    chunk_words = int(input_data.get("chunk_words") or DEFAULT_CHUNK_WORDS)

    raw_chunks = input_data.get("chunks")
    if isinstance(raw_chunks, list) and len(raw_chunks) > 0:
        texts: List[str] = []
        for c in raw_chunks:
            if isinstance(c, dict):
                texts.append(str(c.get("text") or ""))
            else:
                texts.append(str(c))
        r = ingest_chunk_strings(texts, source=source, domain=domain, id_prefix=id_prefix)
        r["chunks_total"] = len([t for t in texts if t.strip()])
    else:
        text = str(input_data.get("text") or "").strip()
        if not text:
            raise ValueError("core.rag_ingest: informe `text` (longo) ou `chunks` (lista de textos)")
        r = ingest_text_as_chunks(
            text,
            source=source,
            domain=domain,
            id_prefix=id_prefix,
            chunk_words=chunk_words,
        )

    return {
        "ok": True,
        "domain": domain,
        "id_prefix": id_prefix,
        "source": source,
        "chunks_ingested": r.get("chunks_ingested", 0),
        "chunks_total": r.get("chunks_total"),
        "errors": r.get("errors") or [],
    }


def _execute_tool_core_eoc_enrich(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tool MCP `core.eoc_enrich` — apenas enrich (RAG + predictive + hints), sem campo `ok`."""
    from core.services.cognitive.eoc import eoc_enrich_from_payload

    return eoc_enrich_from_payload(input_data)


def _execute_tool_core_eoc_decide(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tool MCP `core.eoc_decide` — legado: enrich + `ok: True` (nomenclatura histórica)."""
    from core.services.cognitive.eoc import eoc_decide_from_payload

    return eoc_decide_from_payload(input_data)


def _execute_tool_core_decision_support(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.decision_support` — caminho orbital (ex.: MrFoo): DecisionEngine sem Evora policy.
    """
    from core.services.cognitive_core.context.cognitive_context import CognitiveContext
    from core.services.cognitive_core.mediation.decision_engine import DecisionEngine
    from core.services.cognitive_core.perception.adapters import perception_from_mcp_dict
    from core.services.cognitive_core.reality.builder import RealityStateBuilder

    raw = dict(input_data) if isinstance(input_data, dict) else {}
    ch = raw.get("context_hint")
    ch = dict(ch) if isinstance(ch, dict) else {}
    tid = str(ch.get("tenant_id") or raw.get("tenant_id") or "").strip()
    if tid:
        ch["tenant_id"] = tid
    raw["context_hint"] = ch
    if tid and not str(raw.get("tenant_id") or "").strip():
        raw["tenant_id"] = tid

    q = str(
        raw.get("rag_query")
        or raw.get("descricao_pedido")
        or raw.get("pedido_descricao")
        or raw.get("text")
        or ""
    ).strip()
    if not q:
        q = "contexto_operacional_generico"
    raw["rag_query"] = q

    if not tid:
        logger.warning(
            "core.decision_support: tenant_id ausente no payload/context_hint — RAG híbrido por tenant não aplica"
        )

    src = str(raw.get("source") or "orbital").strip() or "orbital"
    perception = perception_from_mcp_dict(raw, source=src, trace_id=raw.get("trace_id"))
    extra: Dict[str, Any] = {}
    ns = raw.get("rag_namespaces")
    if isinstance(ns, list):
        extra["rag_namespaces"] = [str(x) for x in ns]
    elif isinstance(ns, str) and ns.strip():
        extra["rag_namespaces"] = [s.strip() for s in ns.split(",") if s.strip()]
    ctx = CognitiveContext.from_perception(perception, extra=extra or None)
    builder = RealityStateBuilder(
        default_rag_k=int(raw.get("k", 5) or 5),
        default_namespaces=ctx.rag_namespaces or ["global"],
    )
    reality = builder.build(perception, ctx)
    engine = DecisionEngine()
    decision = engine.decide_orbital_support(perception=perception, reality=reality, ctx=ctx)
    dec_meta = decision.metadata or {}
    ol = reality.operational_live or {}
    return {
        "ok": True,
        "decision": decision.to_dict(),
        "enrich_preview": {
            "rag_hits": len(reality.rag_long_term),
            "namespaces": reality.rag_namespaces,
            "operational_live_keys": list(ol.keys())[:20],
            "dynamic_metrics": reality.dynamic_metrics,
            "impacto_rag": ol.get("impacto_rag"),
            "rag_impacto_resumo": ol.get("rag_impacto_resumo"),
            "rag_query_resolved": q,
            "tenant_id_resolved": tid or None,
            "rag_observability": {
                "rag_used": bool(reality.rag_long_term),
                "rag_sources": list(ol.get("rag_sources_distinct") or []),
                "impacto_rag": ol.get("impacto_rag"),
                "impacto_rag_normalizado": dec_meta.get("impacto_rag_normalizado"),
                "acao": dec_meta.get("acao"),
                "rag_influencia": dec_meta.get("rag_influencia"),
                "rag_context_n": dec_meta.get("rag_context_n"),
                "previsao_atraso": dec_meta.get("previsao_atraso"),
                "previsao_atraso_nivel": dec_meta.get("previsao_atraso_nivel"),
                "previsao_atraso_risco": dec_meta.get("previsao_atraso_risco"),
                "taxa_atraso_historico": dec_meta.get("taxa_atraso_historico"),
                "previsao_atraso_score": dec_meta.get("previsao_atraso_score"),
                "learning_weight_acao": dec_meta.get("learning_weight_acao"),
                "alerta_aprendizado": dec_meta.get("alerta_aprendizado"),
            },
        },
    }


def _execute_tool_core_decision_feedback(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.decision_feedback` — persiste outcome vs decisão prevista (loop de aprendizado).
    """
    from core.services.cognitive_core.learning.decision_feedback import (
        build_predicted_payload,
        record_decision_feedback_event,
    )

    trace_id = str(input_data.get("trace_id") or input_data.get("event_id") or "").strip()
    tenant_id = str(input_data.get("tenant_id") or "").strip()
    outcome = input_data.get("outcome") or input_data.get("resultado") or {}
    decision = input_data.get("decision") or {}
    predicted = input_data.get("predicted") or build_predicted_payload(decision)
    upsert = bool(input_data.get("upsert_vectorstore", False))
    if not tenant_id:
        raise ValueError("decision_feedback: tenant_id é obrigatório")
    rid = record_decision_feedback_event(
        trace_id=trace_id or f"fb:{tenant_id}",
        tenant_id=tenant_id,
        source=str(input_data.get("source") or "api"),
        decision_action=str(decision.get("action") or input_data.get("decision_action") or "unknown"),
        decision_snapshot=decision if isinstance(decision, dict) else {},
        predicted=predicted if isinstance(predicted, dict) else {},
        outcome=outcome if isinstance(outcome, dict) else {},
        upsert_vectorstore=upsert,
    )
    return {"ok": True, "record_id": rid, "predicted": predicted}


def _execute_tool_core_rag_feedback_save(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.rag_feedback_save` — grava feedback operacional na camada RAG operacional (vectorstore).
    """
    from core.services.cognitive_core.rag.rag_feedback import save_rag_feedback as rag_fb_save

    tenant_id = str(input_data.get("tenant_id") or "").strip()
    if not tenant_id:
        raise ValueError("rag_feedback_save: tenant_id é obrigatório")
    query = str(input_data.get("query") or input_data.get("descricao_pedido") or "").strip()
    action = input_data.get("action")
    if action is not None and not isinstance(action, str):
        action = str(action)
    outcome = str(input_data.get("outcome") or input_data.get("resultado_real") or "ok")
    impacto = int(input_data.get("impacto_rag") or 0)
    stored = rag_fb_save(tenant_id, query, action, outcome, impacto_rag=impacto)
    return {"ok": True, "stored": stored}


def _execute_tool_core_autonomy_run_cycle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.autonomy_run_cycle` — dispara o ciclo Fase 3 (padrões → insights → ações → DecisionEngine).
    """
    from core.services.cognitive_core.autonomy.autonomous_loop import run_autonomous_cycle

    tenant_id = str(input_data.get("tenant_id") or "").strip()
    if not tenant_id:
        raise ValueError("autonomy_run_cycle: tenant_id é obrigatório")
    snap = input_data.get("operational_snapshot") or input_data.get("operational_live")
    dm = input_data.get("dynamic_metrics")
    ol: Dict[str, Any] = {}
    if isinstance(snap, dict):
        ol["client_operational_snapshot"] = snap
        ol["operational_snapshot"] = snap
    trace_id = input_data.get("trace_id")
    sctx = input_data.get("strategic_context")
    return run_autonomous_cycle(
        tenant_id=tenant_id,
        operational_live=ol,
        dynamic_metrics=dm if isinstance(dm, dict) else None,
        trace_id=str(trace_id) if trace_id else None,
        strategic_context=sctx if isinstance(sctx, dict) else None,
    )


def _execute_tool_core_strategic_analyze(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.strategic_analyze` — KPI + propostas + RealityState + PatternEngine → opcional DecisionEngine.
    """
    from core.services.cognitive_core.context.cognitive_context import CognitiveContext
    from core.services.cognitive_core.mediation.decision_engine import DecisionEngine
    from core.services.cognitive_core.patterns.pattern_engine import PatternEngine
    from core.services.cognitive_core.perception.adapters import perception_from_mcp_dict
    from core.services.cognitive_core.reality.builder import RealityStateBuilder
    from core.services.cognitive_core.strategic.strategy_engine import run_strategic_analysis

    tenant_id = str(input_data.get("tenant_id") or "").strip()
    if not tenant_id:
        raise ValueError("strategic_analyze: tenant_id é obrigatório")
    economic_payload = input_data.get("economic_payload")
    if not isinstance(economic_payload, dict):
        economic_payload = {}
    snap = input_data.get("operational_snapshot")
    dm = input_data.get("dynamic_metrics")
    ol: Dict[str, Any] = {}
    if isinstance(snap, dict):
        ol["client_operational_snapshot"] = snap
        ol["operational_snapshot"] = snap
    op = dict(economic_payload.get("operational") or {})
    if isinstance(dm, dict):
        op["dynamic_metrics"] = dm
    if isinstance(snap, dict) and snap.get("atraso_medio_segundos") is not None:
        op["atraso_medio_segundos"] = snap.get("atraso_medio_segundos")
    economic_payload["operational"] = op

    pe = PatternEngine()
    matches = pe.run(
        tenant_id=tenant_id,
        operational_live=ol,
        dynamic_metrics=dm if isinstance(dm, dict) else {},
    )

    raw = {
        "text": input_data.get("text") or "strategic:analyze",
        "context_hint": {"tenant_id": tenant_id, "strategic": True},
        "trace_id": input_data.get("trace_id"),
    }
    perception = perception_from_mcp_dict(raw, source="strategic", trace_id=input_data.get("trace_id"))
    ns = input_data.get("rag_namespaces")
    extra: Dict[str, Any] = {}
    if isinstance(ns, list):
        extra["rag_namespaces"] = [str(x) for x in ns]
    elif isinstance(ns, str) and ns.strip():
        extra["rag_namespaces"] = [s.strip() for s in ns.split(",") if s.strip()]
    if not extra.get("rag_namespaces"):
        extra["rag_namespaces"] = ["mrfoo", "global"]
    ctx = CognitiveContext.from_perception(perception, extra=extra)
    builder = RealityStateBuilder(
        default_rag_k=int(input_data.get("k", 5) or 5),
        default_namespaces=ctx.rag_namespaces or ["global"],
    )
    reality = builder.build(perception, ctx)

    obj_prof = input_data.get("objective_profile")
    if not isinstance(obj_prof, dict):
        obj_prof = {}
    top_k = input_data.get("strategy_top_k")
    strategy_top_k: Optional[int]
    if top_k is None:
        strategy_top_k = None
    else:
        try:
            strategy_top_k = max(1, min(50, int(top_k)))
        except (TypeError, ValueError):
            strategy_top_k = None

    analysis = run_strategic_analysis(
        tenant_id=tenant_id,
        economic_payload=economic_payload,
        reality=reality,
        pattern_matches=matches,
        objective_profile=obj_prof,
        strategy_top_k=strategy_top_k,
    )

    out: Dict[str, Any] = {"ok": True, "analysis": analysis}

    if input_data.get("with_decision") and analysis.get("proposals"):
        first = analysis["proposals"][0]
        engine = DecisionEngine()
        dec = engine.decide_strategic_support(
            perception=perception,
            reality=reality,
            ctx=ctx,
            strategy_proposal=first,
        )
        out["decision"] = dec.to_dict()

    return out


def _execute_tool_core_strategy_feedback(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Tool MCP `core.strategy_feedback` — regista impacto previsto vs realizado."""
    from core.services.cognitive_core.strategic.strategy_feedback_store import record_strategy_feedback

    tenant_id = str(input_data.get("tenant_id") or "").strip()
    if not tenant_id:
        raise ValueError("strategy_feedback: tenant_id é obrigatório")
    rid = record_strategy_feedback(
        tenant_id=tenant_id,
        strategy_key=str(input_data.get("strategy_key") or "generic"),
        proposal_id=str(input_data.get("proposal_id") or ""),
        predicted_impact=float(input_data.get("predicted_impact") or 0),
        realized_impact=input_data.get("realized_impact"),
        payload=input_data.get("payload") if isinstance(input_data.get("payload"), dict) else {},
    )
    return {"ok": True, "record_id": rid}


def _execute_tool_core_strategic_advanced(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP `core.strategic_advanced` — multi-loja, precificação dinâmica, expansão (bundle).
    """
    from core.services.cognitive_core.strategic.strategic_advanced_bundle import (
        run_strategic_advanced_bundle,
    )

    tenant_id = str(input_data.get("tenant_id") or "").strip()
    if not tenant_id:
        raise ValueError("strategic_advanced: tenant_id é obrigatório")
    mode = str(input_data.get("mode") or "all")
    stores = input_data.get("stores")
    if not isinstance(stores, list):
        stores = []
    pricing_context = input_data.get("pricing_context")
    expansion_context = input_data.get("expansion_context")
    bundle = run_strategic_advanced_bundle(
        tenant_id=tenant_id,
        mode=mode,
        stores=stores,
        pricing_context=pricing_context if isinstance(pricing_context, dict) else None,
        expansion_context=expansion_context if isinstance(expansion_context, dict) else None,
    )
    return {"ok": True, "bundle": bundle}


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
    safe_config = config if isinstance(config, dict) else {}
    has_messages = isinstance(input_data.get("messages"), list) and len(input_data["messages"]) > 0
    if not has_messages:
        if not prompt_text:
            prompt_text = safe_config.get("prompt_inline")
            if not prompt_text:
                raise ValueError("Runtime 'prompt' requer prompt_text, config.prompt_inline ou input_data.messages")

    # Configurações do LLM
    url = safe_config.get("url", f"{OPENMIND_AI_URL}/chat/completions")
    model = safe_config.get("model", "gpt-4o")
    temperature = safe_config.get("temperature", 0.7)
    max_tokens = safe_config.get("max_tokens", 2000)
    
    # Preparar mensagens para o chat
    if has_messages:
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
    
    plen = len(prompt_text or "")
    logger.info(f"Executando runtime prompt: model={model}, prompt_length={plen}")
    
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
    elif runtime == "mrfoo_graph":
        return _execute_runtime_mrfoo_graph(config, input_data)
    else:
        raise ValueError(f"Runtime desconhecido: {runtime}")


def _execute_runtime_mrfoo_graph(config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Executa ação do Food Knowledge Graph via MrFooAdapter (HTTP ao MrFoo)."""
    from adapters.mrfoo_adapter import (
        graph_status,
        graph_sync_full,
        graph_sync_incremental,
        margin_per_minute,
        complexity_score,
        combo_suggestions,
        new_item_suggestions,
    )
    action = (config.get("action") or "").strip()
    tenant_id = (input_data.get("tenant_id") or "").strip()
    if not tenant_id:
        raise ValueError("mrfoo_graph runtime requer input.tenant_id")
    if action == "status":
        return graph_status(tenant_id)
    if action == "sync_full":
        return graph_sync_full(tenant_id)
    if action == "sync_incremental":
        return graph_sync_incremental(tenant_id)
    if action == "margin_per_minute":
        return margin_per_minute(tenant_id, input_data.get("timeslot"))
    if action == "complexity_score":
        return complexity_score(tenant_id)
    if action == "combo_suggestions":
        return combo_suggestions(tenant_id, input_data.get("timeslot"))
    if action == "new_item_suggestions":
        return new_item_suggestions(tenant_id, int(input_data.get("max_items", 10) or 10))
    raise ValueError(f"mrfoo_graph action desconhecida: {action}")


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
        safe_config = tool_version.config if isinstance(tool_version.config, dict) else {}
        if tool_version.prompt_ref or safe_config.get("prompt_inline"):
            prompt_info = resolve_prompt_info(
                tool_version.prompt_ref,
                config=safe_config
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
        config = safe_config
        
        logger.info(f"[{request_id}][{trace_id}] Executando runtime: {runtime}")
        
        try:
            if tool_name == "core.openmind_process_inbound":
                output_data = _execute_tool_core_openmind_process_inbound(input_data)
            elif tool_name == "core.openmind_analyze_product_image":
                output_data = _execute_tool_core_openmind_analyze_product_image(input_data)
            elif tool_name == "core.openmind_chat_completions":
                output_data = _execute_tool_core_openmind_chat_completions(input_data)
            elif tool_name == "core.rag_query":
                output_data = _execute_tool_core_rag_query(input_data)
            elif tool_name == "core.rag_ingest":
                output_data = _execute_tool_core_rag_ingest(input_data)
            elif tool_name == "core.eoc_enrich":
                output_data = _execute_tool_core_eoc_enrich(input_data)
            elif tool_name == "core.eoc_decide":
                output_data = _execute_tool_core_eoc_decide(input_data)
            elif tool_name == "core.decision_support":
                output_data = _execute_tool_core_decision_support(input_data)
            elif tool_name == "core.decision_feedback":
                output_data = _execute_tool_core_decision_feedback(input_data)
            elif tool_name == "core.rag_feedback_save":
                output_data = _execute_tool_core_rag_feedback_save(input_data)
            elif tool_name == "core.autonomy_run_cycle":
                output_data = _execute_tool_core_autonomy_run_cycle(input_data)
            elif tool_name == "core.strategic_analyze":
                output_data = _execute_tool_core_strategic_analyze(input_data)
            elif tool_name == "core.strategy_feedback":
                output_data = _execute_tool_core_strategy_feedback(input_data)
            elif tool_name == "core.strategic_advanced":
                output_data = _execute_tool_core_strategic_advanced(input_data)
            else:
                output_data = execute_runtime(runtime, config, input_data, prompt_text=prompt_text)
            # Side effects best-effort (learning/telemetry tools)
            if tool_name == "mrfoo.order_feedback":
                # Feedback do MrFoo: armazena contexto + outcome em memória semântica
                # para posterior retrieval no EOC/RAG.
                try:
                    from core.services.learning.order_feedback_service import save_order_feedback

                    save_order_feedback(payload=input_data)
                    output_data = {"status": "ok", "stored": True}
                except Exception as e:
                    # Não falhar a tool call se memória estiver indisponível.
                    output_data = {"status": "ok", "stored": False, "error": str(e)}
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


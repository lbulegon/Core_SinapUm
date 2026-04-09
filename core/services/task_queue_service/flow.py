import logging
import os
import time
from typing import Any, Dict

from app_inbound_events.models import InboundEvent
from core.services.cognitive.eoc import build_cognitive_context
from core.services.cognitive.predictive import prever_riscos
from core.services.learning.decision_log_service import log_decision
from core.services.semantic_cache_service.cache import semantic_query, semantic_store
from core.services.llm_gateway_service.gateway import llm_generate
from core.services.vectorstore_client import vectorstore_search
from core.services.whatsapp_gateway_service.client import WhatsAppGatewayClient, WhatsAppGatewayError
from app_mcp.clients.evora_mcp_client import EvoraMCPClient, PolicyDecision

logger = logging.getLogger(__name__)


def _use_cognitive_orchestrator() -> bool:
    return os.getenv("COGNITIVE_CORE_USE_ORCHESTRATOR", "true").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def _log_event(event_id: str, data: Dict[str, Any]) -> None:
    logger.info("inbound_flow trace_id=%s %s", event_id, data)


def run_event_flow(inbound_event_id: str) -> None:
    """
    Pipeline inbound (WhatsApp / eventos). Por padrão delega ao CognitiveOrchestrator.
    Defina COGNITIVE_CORE_USE_ORCHESTRATOR=false para o caminho legado linha-a-linha.
    """
    if _use_cognitive_orchestrator():
        from core.services.cognitive_core.orchestration.orchestrator import CognitiveOrchestrator

        CognitiveOrchestrator().run_inbound_whatsapp_flow(inbound_event_id)
        return

    # --- Legado (mantido para rollback sem alterar comportamento) ---
    started = time.time()
    ev = InboundEvent.objects.get(event_id=inbound_event_id)
    payload = ev.payload_json or {}
    text = payload.get("text") or payload.get("message") or ""
    user_id = payload.get("user_id") or payload.get("from") or ""
    channel = payload.get("channel") or ev.source
    contract_version = payload.get("contract_version", "v1")
    policy_hint = payload.get("context_hint", {})
    mcp = EvoraMCPClient()
    decision: PolicyDecision = mcp.policy_decide(
        event_id=inbound_event_id,
        channel=channel,
        user_id=user_id,
        text=text,
        context_hint=policy_hint,
        contract_version=contract_version,
    )
    _log_event(inbound_event_id, {
        "stage": "policy_decide",
        "route": decision.route,
        "allow_ai": decision.allow_ai,
        "policy_version": decision.policy_version,
        "contract_version": contract_version,
    })
    cache_context = {
        "route": decision.route,
        "tags": decision.tags or [],
        "template_id": decision.template_id,
        "user_id": user_id,
        "channel": channel,
    }
    cached = semantic_query(intent=text, context=cache_context)
    cognitive_context: Dict[str, Any] = {}
    if cached is not None:
        response_text = cached
        cache_hit = True
    else:
        cache_hit = False
        contexto_rag = vectorstore_search(text, k=5)
        riscos = prever_riscos({**cache_context, "user_text": text, "text": text})
        cognitive_context = build_cognitive_context(cache_context, contexto_rag, riscos, text)
        _log_event(inbound_event_id, {
            "stage": "cognitive",
            "rag_hits": len(contexto_rag),
            "risco_score": riscos.get("score"),
        })
        if decision.allow_ai:
            response_text = llm_generate(
                prompt_input=text,
                context=cognitive_context,
                prompt_version=decision.prompt_version or "v1",
                contract_version=contract_version,
            )
            semantic_store(intent=text, context=cache_context, response=response_text, ttl_seconds=decision.ttl_seconds)
        else:
            response_text = decision.template_text or "Certo — vou encaminhar isso para atendimento."
            semantic_store(intent=text, context=cache_context, response=response_text, ttl_seconds=decision.ttl_seconds)
    _log_event(inbound_event_id, {"stage": "response_ready", "cache_hit": cache_hit, "ttl_seconds": decision.ttl_seconds})

    send_ok = False
    send_error = ""
    try:
        gw = WhatsAppGatewayClient()
        gw_resp = gw.send_message(
            to=user_id,
            text=response_text,
            meta={
                "event_id": inbound_event_id,
                "route": decision.route,
                "policy_version": decision.policy_version,
                "contract_version": contract_version,
                "cache_hit": cache_hit,
            },
        )
        send_ok = True
        _log_event(inbound_event_id, {"stage": "send_message_ok", "gateway": gw_resp})
    except WhatsAppGatewayError as e:
        send_error = str(e)
        _log_event(inbound_event_id, {"stage": "send_message_failed", "error": send_error})
        raise
    finally:
        log_decision(
            event_id=inbound_event_id,
            contexto={
                "cache_context": cache_context,
                "cognitive": cognitive_context if cognitive_context else None,
                "text_preview": (text[:500] if text else ""),
            },
            decisao={
                "route": decision.route,
                "allow_ai": decision.allow_ai,
                "policy_version": decision.policy_version,
                "template_id": decision.template_id,
                "tags": decision.tags or [],
            },
            resultado={
                "cache_hit": cache_hit,
                "send_ok": send_ok,
                "send_error": send_error or None,
                "elapsed_s": round(time.time() - started, 3),
            },
        )

    mcp.domain_append_message(
        event_id=inbound_event_id,
        direction="outbound",
        message_text=response_text,
        metadata={
            "route": decision.route,
            "cache_hit": cache_hit,
            "tags": decision.tags or [],
            "template_id": decision.template_id,
            "policy_version": decision.policy_version,
            "contract_version": contract_version,
        },
        contract_version=contract_version,
    )
    _log_event(inbound_event_id, {"stage": "done", "elapsed": round(time.time() - started, 3)})

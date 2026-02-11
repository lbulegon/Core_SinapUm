import time
from typing import Any, Dict

from app_inbound_events.models import InboundEvent
from core.services.semantic_cache_service.cache import semantic_query, semantic_store
from core.services.llm_gateway_service.gateway import llm_generate
from core.services.whatsapp_gateway_service.client import WhatsAppGatewayClient, WhatsAppGatewayError
from app_mcp.clients.evora_mcp_client import EvoraMCPClient, PolicyDecision


def _log_event(event_id: str, data: Dict[str, Any]) -> None:
    print({"event_id": event_id, **data})


def run_event_flow(inbound_event_id: str) -> None:
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
    if cached is not None:
        response_text = cached
        cache_hit = True
    else:
        cache_hit = False
        if decision.allow_ai:
            response_text = llm_generate(
                prompt_input=text,
                context=cache_context,
                prompt_version=decision.prompt_version or "v1",
                contract_version=contract_version,
            )
            semantic_store(intent=text, context=cache_context, response=response_text, ttl_seconds=decision.ttl_seconds)
        else:
            response_text = decision.template_text or "Certo — vou encaminhar isso para atendimento."
            semantic_store(intent=text, context=cache_context, response=response_text, ttl_seconds=decision.ttl_seconds)
    _log_event(inbound_event_id, {"stage": "response_ready", "cache_hit": cache_hit, "ttl_seconds": decision.ttl_seconds})

    # 5) Envio real via WhatsApp Gateway Service
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
        _log_event(inbound_event_id, {"stage": "send_message_ok", "gateway": gw_resp})
    except WhatsAppGatewayError as e:
        _log_event(inbound_event_id, {"stage": "send_message_failed", "error": str(e)})
        raise

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

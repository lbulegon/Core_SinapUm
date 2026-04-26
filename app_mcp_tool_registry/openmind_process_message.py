"""
Mapeamento entre o contrato do Core (evento canónico + context) e o OpenMind
FastAPI `ProcessMessageRequest` / `ProcessMessageResponse` (agente em /api/v1/process-message).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _extract_incoming_text(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    t = (event or {}).get("text")
    if t is not None and str(t).strip():
        return str(t).strip()
    payload = (event or {}).get("payload")
    if isinstance(payload, dict):
        ptext = payload.get("text")
        if ptext is not None and str(ptext).strip():
            return str(ptext).strip()
    for m in reversed((context or {}).get("last_messages") or []):
        if not isinstance(m, dict):
            continue
        d = str(m.get("direction", "")).lower()
        if d in ("in", "inbound"):
            tx = m.get("text") or ""
            if str(tx).strip():
                return str(tx).strip()
    return ""


def build_process_message_request(event: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Constrói o corpo JSON para POST /api/v1/process-message (esquema ProcessMessageRequest).
    """
    event = event or {}
    context = context or {}
    conv_ctx = context.get("conversation") or {}
    if not isinstance(conv_ctx, dict):
        conv_ctx = {}

    message = _extract_incoming_text(event, context)
    if not message:
        message = "."

    conversation_id = (
        event.get("conversation_id")
        or conv_ctx.get("id")
        or ""
    )
    if not conversation_id:
        raise ValueError(
            "openmind_process_message: é necessário conversation_id no evento ou context.conversation.id"
        )

    user_phone = (
        event.get("from_phone")
        or event.get("from_number")
        or event.get("user_phone")
        or conv_ctx.get("customer_phone")
        or ""
    )
    if not (str(user_phone).strip()):
        raise ValueError(
            "openmind_process_message: é necessário telefone (event.from_phone / user_phone ou context.conversation.customer_phone)"
        )

    user_name = event.get("user_name")
    if user_name is None:
        user_name = conv_ctx.get("customer_name")

    is_group = bool(event.get("is_group"))
    if not is_group:
        ct = str(event.get("chat_type") or "private").lower()
        is_group = ct == "group"

    language = str(event.get("language") or "pt-BR")

    agent_role = event.get("agent_role") or "vendedor"

    metadata: Dict[str, Any] = {
        "canonical_event": {k: v for k, v in event.items() if k != "raw"},
        "last_messages": context.get("last_messages") or [],
    }
    raw_meta = event.get("metadata")
    if isinstance(raw_meta, dict):
        metadata["event_metadata"] = raw_meta

    return {
        "message": message,
        "conversation_id": str(conversation_id),
        "user_phone": str(user_phone).strip(),
        "user_name": user_name,
        "group_id": event.get("group_id"),
        "is_group": is_group,
        "offer_id": event.get("offer_id"),
        "language": language,
        "agent_role": str(agent_role),
        "metadata": metadata,
    }


def map_process_message_response_to_bridge(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte resposta OpenMind (formato agente ProcessMessageResponse ou legado) para
    o dict usado por SuggestionService / app_ai_bridge.
    """
    if not isinstance(data, dict):
        return _fallback_reply()
    if data.get("success") is False and not (data.get("suggested_reply") or data.get("message")):
        return _fallback_reply()

    # Legado: proxy com suggested_reply (sem o modelo agente)
    if data.get("success") and "suggested_reply" in data and "capabilities" not in data:
        return {
            "intent": str(data.get("intent", "unknown")),
            "confidence": float(data.get("confidence", 0.0) or 0.0),
            "suggested_reply": str(data.get("suggested_reply", "") or ""),
            "actions": data.get("actions") if isinstance(data.get("actions"), list) else [],
        }

    # OpenMind agente (ProcessMessageResponse: `message` = resposta ao utilizador)
    if data.get("success") is True and "message" in data:
        reply = str(data.get("message") or "")
        act = data.get("action")
        actions: List[Dict[str, Any]] = []
        if act and str(act).strip().lower() not in ("", "none", "null"):
            actions.append({"name": str(act), "type": "agent_action"})
        extra = data.get("data")
        intent = "chat"
        if isinstance(extra, dict) and extra.get("intent"):
            intent = str(extra["intent"])
        conf = data.get("confidence")
        if conf is None and isinstance(extra, dict) and extra.get("confidence") is not None:
            try:
                conf = float(extra["confidence"])
            except (TypeError, ValueError):
                conf = None
        if conf is None:
            conf = 0.88
        return {
            "intent": intent,
            "confidence": float(conf),
            "suggested_reply": reply,
            "actions": actions,
        }

    logger.warning("Resposta OpenMind inesperada: keys=%s", list(data.keys()))
    return _fallback_reply()


def _fallback_reply() -> Dict[str, Any]:
    return {
        "intent": "unknown",
        "confidence": 0.0,
        "suggested_reply": "Entendi. Vou te ajudar. O que você procura?",
        "actions": [],
    }

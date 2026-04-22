"""
Chef Agnos (Core) — turno conversacional via DecisionEngine orbital (core.decision_support).

Contrato alinhado ao MrFoo: response, confidence, intent, actions_taken, session_id.

Isolamento multi-tenant (hermético): ver tarefas enumeradas em
``services.chef_agno.tenant_isolation_tasks`` (CORE-AGNO-*).
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def run_chef_conversational_turn(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Processa uma mensagem usando o mesmo pipeline MCP `core.decision_support` (sem HTTP interno).

    payload esperado (campos opcionais entre []):
      - text: str (obrigatório para uso útil)
      - user_id, channel, session_id: metadados MrFoo
      - tenant_id: str (recomendado para RAG híbrido por tenant)
      - rag_query: str (default: text)
      - rag_namespaces: list[str] | str
      - operational_snapshot: dict (contexto KDS/operacional)
    """
    from app_mcp_tool_registry.services import _execute_tool_core_decision_support

    raw = dict(payload) if isinstance(payload, dict) else {}
    text = str(raw.get("text") or "").strip()
    tid = str(raw.get("tenant_id") or "").strip()
    ch = raw.get("context_hint")
    if not isinstance(ch, dict):
        ch = {}
    ch = {**ch}
    if tid:
        ch["tenant_id"] = tid
    if raw.get("user_id") is not None:
        ch["user_id"] = raw.get("user_id")
    if raw.get("channel"):
        ch["channel"] = raw.get("channel")
    if raw.get("session_id"):
        ch["session_id"] = raw.get("session_id")
    if raw.get("operational_snapshot") and isinstance(raw.get("operational_snapshot"), dict):
        ch["operational_snapshot"] = raw["operational_snapshot"]

    req: dict[str, Any] = {
        "text": text or "mrfoo:chef_agno",
        "source": "mrfoo",
        "tenant_id": tid,
        "context_hint": ch,
        "rag_query": str(raw.get("rag_query") or text or "contexto_operacional_generico").strip(),
    }
    if raw.get("trace_id"):
        req["trace_id"] = raw["trace_id"]
    ns = raw.get("rag_namespaces")
    if ns:
        req["rag_namespaces"] = ns
    if raw.get("k") is not None:
        try:
            req["k"] = int(raw["k"])
        except (TypeError, ValueError):
            pass

    try:
        out = _execute_tool_core_decision_support(req)
    except Exception as exc:
        logger.exception("run_chef_conversational_turn falhou: %s", exc)
        return {
            "response": "Serviço Chef Agnos no Core indisponível no momento. Tente novamente.",
            "confidence": 0.0,
            "intent": "ERROR",
            "actions_taken": [],
            "session_id": raw.get("session_id"),
            "source": "core_error",
        }

    dec = out.get("decision") if isinstance(out, dict) else None
    dec = dec if isinstance(dec, dict) else {}
    response_text = dec.get("expected_outcome") or dec.get("response_text")
    if not response_text:
        action = str(dec.get("action") or "orbital_support")
        meta = dec.get("metadata") or {}
        motivo = meta.get("motivo") if isinstance(meta, dict) else None
        response_text = motivo or f"Análise operacional ({action})."
    actions = [str(dec.get("action") or "decision_support")]
    meta = dec.get("metadata") if isinstance(dec.get("metadata"), dict) else {}
    if isinstance(meta.get("acao"), str) and meta.get("acao") not in actions:
        actions.append(meta["acao"])

    return {
        "response": str(response_text),
        "confidence": float(dec.get("confidence") or 0.0),
        "intent": str(dec.get("action") or "CHEF_CORE_ORBITAL"),
        "actions_taken": actions,
        "session_id": raw.get("session_id"),
        "source": "core_decision_support",
    }

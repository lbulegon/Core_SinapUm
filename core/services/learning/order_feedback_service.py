import json
import os
import time
from typing import Any, Dict, Optional

import requests


def _vectorstore_url() -> str:
    """
    Resolve a URL do vectorstore_service (FastAPI + FAISS).
    Default pensado para execução dentro do docker-compose do Core.
    """
    explicit = os.getenv("VECTORSTORE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")

    port = os.getenv("VECTORSTORE_PORT", "8010").strip()
    # Dentro do compose, o host é o service name.
    return f"http://vectorstore_service:{port}"


def _safe_str(v: Any) -> str:
    return "" if v is None else str(v)


def save_order_feedback(payload: Dict[str, Any]) -> None:
    """
    Best-effort: armazena payload (context + plano + outcome) como "texto" no FAISS.

    Contrato mínimo aceito (flexível):
    - tenant_id (string ou number)
    - pedido_id (string ou number)
    - context (obj) opcional
    - plan (obj) opcional
    - outcome (obj) opcional
    - success/status (opc.)
    """
    tenant_id = _safe_str(payload.get("tenant_id") or payload.get("tenant") or payload.get("tenantId")).strip()
    pedido_id = _safe_str(payload.get("pedido_id") or payload.get("pedido") or payload.get("order_id") or payload.get("orderId")).strip()

    if not tenant_id or not pedido_id:
        raise ValueError("save_order_feedback: tenant_id e pedido_id são obrigatórios")

    # Campos opcionais (aceita variações de nomes para não travar integração)
    context = payload.get("context") or payload.get("context_operacional") or payload.get("contexto_operacional") or {}
    plan = payload.get("plan") or payload.get("decision_plan") or payload.get("decisao") or payload.get("plano") or {}
    outcome = payload.get("outcome") or payload.get("resultado") or payload.get("resultado_operacional") or payload.get("outcome_operacional") or {}

    success: Optional[bool] = payload.get("success")
    status = payload.get("status") or payload.get("status_final") or outcome.get("status_final")

    stored_doc = {
        "tenant_id": tenant_id,
        "pedido_id": pedido_id,
        "context": context,
        "plan": plan,
        "outcome": outcome,
        "success": success,
        "status": status,
        "stored_at": int(time.time()),
        # Mantém o payload original pra facilitar debugging/evolução.
        "raw": payload,
    }

    doc_id = f"mrfoo.order_feedback:{tenant_id}:{pedido_id}:{int(time.time() * 1000)}"
    text = json.dumps(stored_doc, ensure_ascii=False)

    url = f"{_vectorstore_url()}/upsert"
    resp = requests.post(
        url,
        json={"id": doc_id, "text": text},
        timeout=float(os.getenv("VECTORSTORE_TIMEOUT", "10")),
    )
    resp.raise_for_status()


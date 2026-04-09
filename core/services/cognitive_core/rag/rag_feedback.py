"""
Persistência de feedback operacional no vectorstore (camada operacional por tenant).
O texto é JSON para o ranker reutilizar `_metadata_from_hit_text` / impacto_fluxo.
"""
from __future__ import annotations

import json
import logging
import uuid
from typing import Optional

from core.services.cognitive_core.rag.hybrid_rag import _sanitize_tenant_id
from core.services.vectorstore_client import vectorstore_upsert

logger = logging.getLogger(__name__)


def save_rag_feedback(
    tenant_id: str,
    query: str,
    action: Optional[str],
    outcome: str,
    *,
    impacto_rag: int = 0,
) -> bool:
    """
    Grava um documento de aprendizagem na camada operacional do tenant.

    outcome: \"ok\", \"atraso\" ou \"falha\" (outros → \"ok\").
    """
    tid = _sanitize_tenant_id(tenant_id)
    if not tid:
        logger.warning("save_rag_feedback: tenant_id inválido")
        return False
    oc = (outcome or "ok").strip().lower()
    if oc not in ("ok", "atraso", "falha"):
        oc = "ok"
    flux = "alto" if oc in ("atraso", "falha") else "medio"
    doc = {
        "type": "rag_feedback",
        "acao": (action or "")[:256],
        "outcome": oc,
        "impacto_fluxo": flux,
        "tenant_id": tid,
        "query": (query or "")[:2000],
        "impacto_rag": int(impacto_rag or 0),
    }
    text = json.dumps(doc, ensure_ascii=False)
    fid = f"tenant:{tid}:operacional:feedback:{uuid.uuid4()}"
    ok = vectorstore_upsert(fid, text)
    if not ok:
        logger.debug("save_rag_feedback: upsert falhou tenant=%s", tid)
    return ok

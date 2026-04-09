"""
RAG como variável operacional: extrai impacto de fluxo dos documentos indexados (JSON no vectorstore).
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Tuple

from core.services.cognitive_core.perception.input import PerceptionInput

logger = logging.getLogger(__name__)

_IMPACTO_MAP = {"alto": 2, "medio": 1, "médio": 1, "baixo": 0, "baixa": 0}


def rag_query_text_from_perception(perception: PerceptionInput) -> str:
    """
    Texto usado na busca semântica: prioriza descrição do pedido / rag_query explícito.
    """
    raw = perception.raw_data or {}
    q = (
        (
            raw.get("rag_query")
            or raw.get("descricao_pedido")
            or raw.get("pedido_descricao")
            or ""
        ).strip()
        or (perception.text or "").strip()
    )
    return q


def _parse_rag_doc_text(text: str) -> Dict[str, Any]:
    if not text or not str(text).strip().startswith("{"):
        return {}
    try:
        d = json.loads(text)
        return d if isinstance(d, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def impacto_score_from_doc(doc: Dict[str, Any]) -> int:
    flux = doc.get("impacto_fluxo")
    if isinstance(flux, str):
        return int(_IMPACTO_MAP.get(flux.strip().lower(), 0))
    return 0


def compute_impacto_rag_from_hits(hits: List[dict]) -> Tuple[int, Dict[str, Any]]:
    """
    Soma impacto por hit (alto=2, medio=1, baixo=0) a partir do JSON armazenado no vectorstore.
    """
    total = 0
    counts = {"alto": 0, "medio": 0, "baixo": 0, "desconhecido": 0}
    for h in hits or []:
        raw_txt = (h or {}).get("text") or ""
        doc = _parse_rag_doc_text(raw_txt)
        if not doc:
            counts["desconhecido"] += 1
            continue
        flux = str(doc.get("impacto_fluxo") or "").lower()
        if flux in ("alto",):
            counts["alto"] += 1
        elif flux in ("medio", "médio"):
            counts["medio"] += 1
        elif flux in ("baixo", "baixa"):
            counts["baixo"] += 1
        else:
            counts["desconhecido"] += 1
        total += impacto_score_from_doc(doc)
    return total, {
        "hits_considered": len(hits or []),
        "counts": counts,
        "score_total": total,
    }

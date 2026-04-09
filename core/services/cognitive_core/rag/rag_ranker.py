"""
Ranking de hits RAG com peso por camada, impacto operacional (JSON no text) e aprendizagem por ação.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.rag.rag_adaptive_weights import get_namespace_weight
from core.services.cognitive_core.rag.rag_learning import get_action_performance


def _metadata_from_hit_text(text: Optional[str]) -> Dict[str, Any]:
    if not text or not str(text).strip().startswith("{"):
        return {}
    try:
        d = json.loads(text)
        return d if isinstance(d, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def rank_rag_results(
    results: List[Dict[str, Any]],
    *,
    tenant_id: Optional[str] = None,
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    tid = str(tenant_id or "").strip() or None
    ranked: List[Dict[str, Any]] = []
    for item in results or []:
        base = float((item or {}).get("score") or 0.0)
        st = str((item or {}).get("source_type") or "global")
        namespace_w = get_namespace_weight(st)
        meta = _metadata_from_hit_text((item or {}).get("text"))
        action_key = meta.get("acao")
        if tid and action_key not in (None, ""):
            learning_w = get_action_performance(tid, str(action_key))
        else:
            learning_w = 1.0
        impacto_bonus = 0.0
        flux = str(meta.get("impacto_fluxo") or "").lower()
        if flux == "alto":
            impacto_bonus += 0.4
        elif flux in ("medio", "médio"):
            impacto_bonus += 0.2
        final = (base * namespace_w * learning_w) + impacto_bonus
        row = dict(item)
        row["final_score"] = round(final, 6)
        row["_parsed_metadata"] = {
            "impacto_fluxo": meta.get("impacto_fluxo"),
            "type": meta.get("type"),
            "complexidade": meta.get("complexidade"),
            "acao": meta.get("acao"),
        }
        row["_rank_weights"] = {
            "namespace": namespace_w,
            "learning": learning_w,
            "impacto_bonus": impacto_bonus,
        }
        ranked.append(row)

    ranked.sort(key=lambda x: float(x.get("final_score") or 0.0), reverse=True)
    return ranked[: max(1, top_n)]


def impacto_total_from_ranked(ranked: List[Dict[str, Any]]) -> int:
    """Soma impacto discreto (alto=2, medio=1) a partir do JSON em text."""
    total = 0
    for item in ranked or []:
        meta = _metadata_from_hit_text((item or {}).get("text"))
        flux = str(meta.get("impacto_fluxo") or "").lower()
        if flux == "alto":
            total += 2
        elif flux in ("medio", "médio"):
            total += 1
    return total

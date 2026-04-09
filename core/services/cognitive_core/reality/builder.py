"""
Constrói RealityState a partir de PerceptionInput + CognitiveContext.
Fase 2: operational_live + dynamic_metrics (Segundidade forte); RAG permanece memória, não realidade.
RAG híbrido (tenant + operacional + global) quando há tenant_id + query.
"""
from __future__ import annotations

from typing import List, Optional

from core.services.cognitive_core.context.cognitive_context import CognitiveContext
from core.services.cognitive_core.perception.input import PerceptionInput
from core.services.cognitive_core.rag.hybrid_rag import hybrid_rag_search
from core.services.cognitive_core.rag.rag_ranker import impacto_total_from_ranked, rank_rag_results
from core.services.cognitive_core.reality.graph_context import graph_snippet_for_tenant
from core.services.cognitive_core.reality.operational_snapshot import (
    build_operational_live_layer,
    compute_dynamic_metrics,
)
from core.services.cognitive_core.reality.rag_operational import (
    compute_impacto_rag_from_hits,
    rag_query_text_from_perception,
)
from core.services.cognitive_core.reality.state import RealityState
from core.services.vectorstore_client import vectorstore_search


def _distinct_rag_sources(hits: List[dict]) -> List[str]:
    seen: set[str] = set()
    for h in hits or []:
        st = (h or {}).get("source_type") or (h or {}).get("_namespace")
        if st:
            seen.add(str(st))
    return sorted(seen)


class RealityStateBuilder:
    """
    Agrega RAG (com namespace), operacional (hint) e graph (stub/extensível).
    """

    def __init__(
        self,
        *,
        default_rag_k: int = 5,
        default_namespaces: Optional[List[str]] = None,
    ):
        self.default_rag_k = default_rag_k
        self.default_namespaces = default_namespaces or []

    def build(
        self,
        perception: PerceptionInput,
        ctx: CognitiveContext,
        *,
        rag_k: Optional[int] = None,
        extra_namespaces: Optional[List[str]] = None,
    ) -> RealityState:
        hint = perception.context_hint()
        operational = {
            **hint,
            "user_id": perception.user_id,
            "channel": perception.channel,
            "contract_version": perception.contract_version,
        }
        tid = str(hint.get("tenant_id") or hint.get("tenant") or "").strip() or None
        operational_live = build_operational_live_layer(operational, tenant_id=tid)
        dynamic_metrics = operational_live.pop("dynamic_metrics_derived", {}) or compute_dynamic_metrics(
            operational_live
        )

        namespaces = list(
            dict.fromkeys(
                (extra_namespaces or [])
                + self.default_namespaces
                + (ctx.rag_namespaces or [])
            )
        )
        if not namespaces:
            namespaces = ["global"]

        k = rag_k if rag_k is not None else self.default_rag_k
        q = (rag_query_text_from_perception(perception) or perception.text or "").strip()

        merged_hits: List[dict] = []
        rag_context: List[dict] = []

        if q and tid:
            raw = hybrid_rag_search(q, tid, top_k_per_source=k)
            ranked = rank_rag_results(raw, tenant_id=tid, top_n=max(k, 8))
            merged_hits = ranked
            rag_context = ranked[:5]
            impacto_rag = impacto_total_from_ranked(ranked)
            operational_live["impacto_rag"] = impacto_rag
            operational_live["rag_impacto_resumo"] = {
                "modo": "hybrid",
                "hits_ranked": len(ranked),
                "impacto_total": impacto_rag,
            }
            operational_live["rag_sources_distinct"] = _distinct_rag_sources(merged_hits)
        else:
            seen_ids: set[str] = set()
            for ns in namespaces:
                prefix = f"{ns}:" if ns != "global" else None
                hits = vectorstore_search(q, k=k, include_text=True, id_prefix=prefix)
                for h in hits:
                    hid = str(h.get("id", ""))
                    if not hid or hid in seen_ids:
                        continue
                    seen_ids.add(hid)
                    row = dict(h)
                    row["_namespace"] = ns
                    merged_hits.append(row)

            if q:
                gastro_hits = vectorstore_search(
                    q, k=k, include_text=True, id_prefix="sinapum.rag.gastronomia"
                )
                for h in gastro_hits or []:
                    hid = str((h or {}).get("id", ""))
                    if not hid or hid in seen_ids:
                        continue
                    seen_ids.add(hid)
                    row = dict(h)
                    row["_namespace"] = "gastronomia"
                    merged_hits.append(row)

            impacto_rag, rag_imp_resumo = compute_impacto_rag_from_hits(merged_hits)
            operational_live["impacto_rag"] = impacto_rag
            operational_live["rag_impacto_resumo"] = rag_imp_resumo
            rag_context = merged_hits[:5]
            operational_live["rag_sources_distinct"] = _distinct_rag_sources(merged_hits)

        tenant = str(hint.get("tenant_id") or hint.get("tenant") or "")
        graph = graph_snippet_for_tenant(tenant) if tenant else {"available": False, "rows": []}

        return RealityState(
            operational=operational,
            operational_live=operational_live,
            dynamic_metrics=dynamic_metrics,
            rag_long_term=merged_hits,
            rag_context=rag_context,
            graph_structural=graph,
            rag_namespaces=namespaces,
        )

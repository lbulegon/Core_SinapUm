"""
EOC — apenas ENRIQUECIMENTO (RAG + heurísticas preditivas).
Decisão mediadora vive em cognitive_core.mediation.DecisionEngine.

Compatibilidade:
- `eoc_decide_from_payload` mantém contrato MCP legado (campo `ok: True`).
- `eoc_enrich_bundle` / `eoc_enrich_from_payload` são a nomenclatura correta (sem "decide").
"""
from typing import Any, Dict, List

from core.services.cognitive.predictive import prever_riscos
from core.services.vectorstore_client import vectorstore_search


def build_cognitive_context(
    base_context: Dict[str, Any],
    rag_results: List[Dict[str, Any]],
    riscos: Dict[str, Any],
    user_text: str,
) -> Dict[str, Any]:
    out = dict(base_context)
    out["rag_results"] = rag_results
    out["riscos_previstos"] = riscos
    out["user_text"] = user_text
    out["cognitive_version"] = "v1"
    return out


def eoc_enrich_bundle(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Núcleo de enrich: text/query, context_hint, k, id_prefix (namespace RAG opcional).
    Retorno SEM campo `ok` — uso interno e tool `core.eoc_enrich`.
    """
    text = (input_data.get("text") or input_data.get("query") or "").strip()
    hint = input_data.get("context_hint") or input_data.get("context") or {}
    if not isinstance(hint, dict):
        hint = {}
    k = int(input_data.get("k", 5) or 5)
    id_prefix = input_data.get("id_prefix") or input_data.get("rag_id_prefix")
    if isinstance(id_prefix, str):
        id_prefix = id_prefix.strip() or None
    else:
        id_prefix = None

    pre = input_data.get("precomputed_rag")
    if pre is not None and isinstance(pre, list):
        rag = list(pre)
    elif text:
        rag = vectorstore_search(text, k=k, include_text=True, id_prefix=id_prefix)
    else:
        rag = []
    ctx = {**hint, "user_text": text, "text": text}
    riscos = prever_riscos(ctx)
    enriched = build_cognitive_context(hint, rag, riscos, text)

    hints: Dict[str, Any] = {}
    if riscos.get("score", 0) >= 0.44:
        hints["prioridade_delta"] = 1
    if any(r.get("tipo") == "atencao_cliente" for r in riscos.get("riscos") or []):
        hints["atencao_cliente"] = True

    return {
        "rag": rag,
        "riscos": riscos,
        "enriched_context": enriched,
        "hints": hints,
    }


def eoc_enrich_from_payload(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Alias explícito para MCP / chamadas externas nomeadas 'enrich'."""
    return eoc_enrich_bundle(input_data)


def eoc_decide_from_payload(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Contrato legado MCP `core.eoc_decide`: mesmo enrich + `ok: True`.
    Não executa decisão de negócio — apenas enriquecimento com nome histórico.
    """
    out = eoc_enrich_bundle(input_data)
    return {"ok": True, **out}

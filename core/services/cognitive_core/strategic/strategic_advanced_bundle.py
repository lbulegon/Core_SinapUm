"""
Orquestra otimização multi-loja, precificação dinâmica e sinais de expansão num único payload MCP.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.services.cognitive_core.strategic.dynamic_pricing import compute_dynamic_price_recommendation
from core.services.cognitive_core.strategic.expansion_automation import evaluate_expansion_readiness
from core.services.cognitive_core.strategic.multi_store_optimizer import analyze_multi_store_portfolio
from core.services.cognitive_core.strategic.strategic_learning import get_tenant_calibration


def run_strategic_advanced_bundle(
    *,
    tenant_id: str,
    mode: str = "all",
    stores: Optional[List[Dict[str, Any]]] = None,
    pricing_context: Optional[Dict[str, Any]] = None,
    expansion_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    mode: all | multi_store | pricing | expansion
    """
    m = (mode or "all").strip().lower()
    out: Dict[str, Any] = {"tenant_id": tenant_id, "mode": m}

    if m in ("all", "multi_store"):
        out["multi_store"] = analyze_multi_store_portfolio(list(stores or []))

    if m in ("all", "pricing"):
        pc = dict(pricing_context or {})
        cal = get_tenant_calibration(str(tenant_id))
        out["dynamic_pricing"] = compute_dynamic_price_recommendation(
            margem_media_pct=float(pc.get("margem_media_pct") or 0),
            operational_load=float(pc.get("operational_load") or 0),
            atraso_medio_segundos=float(pc.get("atraso_medio_segundos") or 0),
            custo_atraso_estimado=float(pc.get("custo_atraso_estimado") or 0),
            demand_elasticity=pc.get("demand_elasticity"),
            calibration=cal,
        )

    if m in ("all", "expansion"):
        ec = dict(expansion_context or {})
        out["expansion"] = evaluate_expansion_readiness(
            margem_media_pct=float(ec.get("margem_media_pct") or 0),
            operational_load=float(ec.get("operational_load") or 0),
            eficiencia_operacional=float(ec.get("eficiencia_operacional") or 0),
            atraso_medio_segundos=float(ec.get("atraso_medio_segundos") or 0),
            receita_trailing=float(ec.get("receita_trailing") or 0),
            strategic_stability_score=ec.get("strategic_stability_score"),
        )

    return out

"""
Simulação leve antes de executar ação autónoma (determinística, sem LLM).
Estimativas de impacto em atraso / throughput para comparar candidatos.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from core.services.cognitive_core.actions.action_generator import ActionProposal
def simulate_autonomy_proposal(
    proposal: ActionProposal,
    *,
    dynamic_metrics: Optional[Dict[str, Any]] = None,
    operational_live: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Retorna métricas comparáveis entre candidatos:
    - delay_reduction_pct_est: redução estimada de pressão de atraso (%)
    - throughput_gain_pct_est: ganho estimado de throughput (%)
    - margin_pressure: -1 a 1 (negativo = pode pressionar margem)
    - composite: score 0–1 para ranking
    """
    dm = dynamic_metrics or {}
    ol = operational_live or {}
    load = float(dm.get("estimated_load") or 0)
    bottleneck = dm.get("bottleneck_hint") or ol.get("gargalo_hint")

    delay_red = 5.0
    tp_gain = 4.0
    margin_p = 0.0

    key = proposal.action_key
    if key == "bump_kitchen_priority":
        delay_red = 12.0 + 8.0 * load
        tp_gain = 10.0 + 5.0 * load
        margin_p = -0.05
    elif key == "suggest_prep_parallel":
        delay_red = 9.0 + 6.0 * load
        tp_gain = 8.0
        margin_p = -0.02
    elif key == "shed_load_alert":
        delay_red = 6.0
        tp_gain = 5.0
        margin_p = 0.0
    elif key == "throughput_recovery_check":
        delay_red = 4.0
        tp_gain = 14.0 if bottleneck else 8.0
        margin_p = 0.0
    elif key == "prioritize_low_prep_items":
        delay_red = 15.0 + 5.0 * load
        tp_gain = 12.0
        margin_p = 0.02
    elif key == "maintain_policy":
        delay_red = 2.0
        tp_gain = 2.0
        margin_p = 0.05
    elif key == "audit_decision_quality":
        delay_red = 3.0
        tp_gain = 4.0
        margin_p = 0.0

    # normalizar para composite (0–1)
    composite = min(
        1.0,
        (delay_red / 22.0) * 0.45 + (tp_gain / 18.0) * 0.45 + max(0.0, 0.1 - abs(margin_p)) * 0.1,
    )

    return {
        "action_key": key,
        "delay_reduction_pct_est": round(delay_red, 2),
        "throughput_gain_pct_est": round(tp_gain, 2),
        "margin_pressure": round(margin_p, 3),
        "composite": round(composite, 4),
        "notes": "heuristic_simulation_v1",
    }

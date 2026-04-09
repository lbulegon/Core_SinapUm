"""
Precificação dinâmica: delta % sugerido com limites, usando carga, atraso, margem e calibração (elasticidade).
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from core.services.cognitive_core.strategic.strategy_simulator import simulate_price_change


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def compute_dynamic_price_recommendation(
    *,
    margem_media_pct: float,
    operational_load: float = 0.0,
    atraso_medio_segundos: float = 0.0,
    custo_atraso_estimado: float = 0.0,
    demand_elasticity: Optional[float] = None,
    calibration: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Devolve delta_pct recomendado (pode ser negativo para promoção), com teto e simulação rápida.

    - Carga/atraso altos: pequeno aumento para desacelerar fila (se margem permitir) ou manter.
    - Carga baixa: leve promoção para volume.
    - Margem muito baixa: prioriza recuperação de margem com delta moderado.
    """
    cal = calibration or {}
    elast = demand_elasticity
    if elast is None:
        base_e = -0.6
        scale = float(cal.get("elasticity_scale", 1.0))
        elast = max(-1.2, min(-0.25, base_e * scale))
    m = _f(margem_media_pct)
    load = max(0.0, min(1.0, _f(operational_load)))
    delay_s = max(0.0, _f(atraso_medio_segundos))
    delay_norm = min(1.0, delay_s / 1200.0)  # 20 min ref.

    delta = 0.0
    rationale: list[str] = []

    if m < 18:
        delta += 2.5
        rationale.append("Margem agregada baixa — inclinar recuperação.")
    elif m > 35:
        delta -= 1.0
        rationale.append("Margem confortável — espaço para promoção leve.")

    if load > 0.82 or delay_norm > 0.55:
        delta += min(3.0, 1.5 + load * 2.0 + delay_norm * 1.5)
        rationale.append("Carga e/ou atraso elevados — preço pode modular procura.")
    elif load < 0.42:
        delta -= min(4.0, 2.0 + (0.5 - load) * 3.0)
        rationale.append("Carga baixa — incentivar volume.")

    if custo_atraso_estimado > 0 and delay_norm > 0.4:
        ref_rec = max(500.0, m * 80.0)
        delta += min(2.0, 0.5 + min(1.0, custo_atraso_estimado / max(ref_rec, 1.0)))
        rationale.append("Custo de atraso material — refletir no preço ou mix.")

    cap = float(os.getenv("SINAPUM_DYNAMIC_PRICE_CAP_PCT", "7"))
    floor = float(os.getenv("SINAPUM_DYNAMIC_PRICE_FLOOR_PCT", "-6"))
    delta = max(floor, min(cap, delta))

    receita_base_sim = max(1000.0, m * 100.0)
    sim = simulate_price_change(
        receita_base=receita_base_sim,
        margem_pct_base=m,
        price_delta_pct=delta,
        demand_elasticity=elast,
    )

    return {
        "delta_pct_recomendado": round(delta, 2),
        "demand_elasticity_usada": round(elast, 4),
        "limites": {"cap_pct": cap, "floor_pct": floor},
        "simulacao_resumo": {
            "receita_depois_vs_antes_pct": round(
                (sim.receita_depois - sim.receita_antes) / max(sim.receita_antes, 1e-6) * 100.0,
                3,
            ),
            "margem_depois": sim.margem_depois,
            "demanda_indice_depois": sim.demanda_indice_depois,
        },
        "rationale": rationale,
    }

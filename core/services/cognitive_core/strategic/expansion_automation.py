"""
Sinais para expansão automatizada (nova loja / linha / canal): prontidão vs risco operacional.
"""
from __future__ import annotations

from typing import Any, Dict, Optional


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _receita_ref(rec: float) -> float:
    return max(50_000.0, rec * 2.0) if rec > 0 else 100_000.0


def evaluate_expansion_readiness(
    *,
    margem_media_pct: float,
    operational_load: float = 0.0,
    eficiencia_operacional: float = 0.0,
    atraso_medio_segundos: float = 0.0,
    receita_trailing: float = 0.0,
    strategic_stability_score: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Score 0–1 e recomendação: expandir / preparar / adiar.
    """
    m = _f(margem_media_pct)
    load = max(0.0, min(1.0, _f(operational_load)))
    eff = max(0.0, min(1.0, _f(eficiencia_operacional)))
    delay = _f(atraso_medio_segundos)
    delay_n = min(1.0, delay / 1500.0)
    rec = max(0.0, _f(receita_trailing))
    stab = strategic_stability_score
    if stab is None:
        stab = 0.5 + 0.2 * eff - 0.15 * load - 0.1 * delay_n
    stab = max(0.0, min(1.0, _f(stab)))

    # score composto
    score = (
        0.22 * min(1.0, m / 30.0)
        + 0.18 * (1.0 - load)
        + 0.2 * eff
        + 0.15 * (1.0 - delay_n)
        + 0.15 * stab
        + 0.1 * min(1.0, rec / max(_receita_ref(rec), 1.0))
    )
    score = max(0.0, min(1.0, score))

    if load > 0.85 or delay_n > 0.65:
        decision = "adiar"
        motivo = "Carga operacional ou atraso elevados — consolidar antes de expandir."
    elif score >= 0.62 and m >= 20 and load < 0.68:
        decision = "expandir"
        motivo = "Saúde financeira e operação estáveis — candidato a nova capacidade."
    elif score >= 0.48:
        decision = "preparar"
        motivo = "Sinais mistos — pilotar playbook e métricas antes de compromisso maior."
    else:
        decision = "adiar"
        motivo = "Score de prontidão abaixo do limiar — reforçar margem e throughput."

    return {
        "readiness_score": round(score, 4),
        "decision": decision,
        "motivo": motivo,
        "sinais": {
            "margem_media_pct": m,
            "operational_load": load,
            "eficiencia_operacional": eff,
            "atraso_medio_segundos": delay,
            "receita_trailing": rec,
            "stability_proxy": round(stab, 4),
        },
        "proposals_hint": [
            {
                "tipo": "expansao",
                "acao": "nova_unidade_piloto" if decision == "expandir" else "reavaliar_em_30d",
                "risco": "high" if load > 0.75 else "medium",
            }
        ],
    }

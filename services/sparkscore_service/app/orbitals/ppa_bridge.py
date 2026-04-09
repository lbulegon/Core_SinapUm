"""
Ponte PPA ↔ pipeline de orbitais (Creative Engine).

Deriva antecipação de ação a partir de emotional / semiotic / cognitive e,
se houver, modula com score_pressao do environmental_indiciary (integração passiva).
Não duplica o motor cognitivo 0–6 nem exige classificador orbital separado.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.orbitals.orbital_result import OrbitalResult


def _result_map(results: List[OrbitalResult]) -> Dict[str, OrbitalResult]:
    return {r.orbital_id: r for r in results}


def gerar_ppa_ambiental(state: str, score: float) -> float:
    """
    Potencial prévio de ação (PPA) a partir do estado indiciário e score (0–1).
    Versão inicial em escala 0.2–0.95.
    """
    _ = score  # reservado para versões futuras (ex. calibrar pela magnitude)
    if state == "colapso":
        return 0.95
    if state == "sobrecarga":
        return 0.85
    if state == "pressao":
        return 0.7
    if state == "atencao":
        return 0.5
    return 0.2


def compute_pipeline_ppa(
    orbitals_results: List[OrbitalResult],
    pipeline_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Calcula sinal de PPA / antecipação de ação a partir dos orbitais já executados.

    - base: urgência emocional, alinhamento goal×texto, penalidade de sobrecarga cognitiva
    - modulação ambiental (opcional): pressão reduz antecipação “lisa” (ruído operacional)
    """
    cfg = pipeline_config or {}
    bridge = cfg.get("ppa_bridge") or {}
    alpha = float(bridge.get("pressure_dampening_alpha", 0.12))

    by_id = _result_map(orbitals_results)

    emotional = by_id.get("emotional")
    semiotic = by_id.get("semiotic")
    cognitive = by_id.get("cognitive")
    env = by_id.get("environmental_indiciary")

    urgency = 0.0
    if emotional and emotional.raw_features:
        urgency = float(emotional.raw_features.get("urgency_score") or 0.0)

    goal_match = 0.0
    if semiotic and semiotic.raw_features:
        goal_match = float(semiotic.raw_features.get("goal_match") or 0.0)

    clutter = 0.0
    if cognitive and cognitive.raw_features:
        wc = float(cognitive.raw_features.get("word_count") or 0)
        ideal = float(cognitive.raw_features.get("ideal_limit") or 20)
        if ideal > 0 and wc > ideal:
            clutter = min(1.0, (wc - ideal) / ideal)

    base = 0.45 * urgency + 0.38 * goal_match + 0.17 * max(0.0, 1.0 - clutter)
    base = max(0.0, min(1.0, base))

    sp: Optional[float] = None
    estado: Optional[str] = None
    combined = base

    if env and env.raw_features:
        raw = env.raw_features.get("score_pressao")
        if raw is not None:
            sp = float(raw)
            sp = max(0.0, min(1.0, sp))
            estado = env.raw_features.get("estado_ambiental")
            combined = base * max(0.0, 1.0 - alpha * sp)
            combined = max(0.0, min(1.0, combined))

    if combined >= 0.65:
        status, stage = "ativo", "ativado"
    elif combined >= 0.4:
        status, stage = "nascente", "nasce"
    else:
        status, stage = "inativo", None

    env_mod: Optional[Dict[str, Any]] = None
    ppa_ambiental: Optional[float] = None
    if sp is not None:
        env_mod = {
            "score_pressao": sp,
            "estado_ambiental": estado,
            "factor_aplicado": round((combined / base) if base > 1e-9 else 1.0, 4),
        }
    if env and env.raw_features:
        est = env.raw_features.get("estado_ambiental")
        sp2 = env.raw_features.get("score_pressao")
        if est is not None and sp2 is not None:
            ppa_ambiental = gerar_ppa_ambiental(str(est), float(sp2))

    return {
        "status": status,
        "stage": stage,
        "confidence": round(combined, 4),
        "antecipacao_acao": round(combined, 4),
        "antecipacao_base": round(base, 4),
        "environmental_modulation": env_mod,
        "ambiental": ppa_ambiental,
    }

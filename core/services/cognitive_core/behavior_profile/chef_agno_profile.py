"""
Perfil Chef Agno: prioriza simplicidade operacional, tempo, risco controlado e padronização.
Não chama LLM — apenas combina sinais de RealityState + riscos EOC.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from core.services.cognitive_core.reality.state import RealityState


class ChefAgnoProfile:
    """
    Pesos explícitos (fine-tuning lógico): ajuste via env ou constantes.
    """

    W_SIMPLICITY = 0.25
    W_TIME = 0.30
    W_RISK = 0.30
    W_STANDARD = 0.15

    @classmethod
    def risk_level_from_score(cls, risco_score: float) -> str:
        if risco_score >= 0.65:
            return "high"
        if risco_score >= 0.35:
            return "medium"
        return "low"

    @classmethod
    def expected_outcome_text(
        cls,
        *,
        action: str,
        hints: Dict[str, Any],
        riscos: Dict[str, Any],
        reality: RealityState,
    ) -> str:
        parts: List[str] = []
        dm = reality.dynamic_metrics or {}
        if dm.get("bottleneck_hint"):
            parts.append(f"Operação: possível gargalo ({dm['bottleneck_hint']}).")
        if hints.get("prioridade_delta"):
            parts.append("Esperado: ajuste de prioridade na fila sugerido.")
        if hints.get("atencao_cliente"):
            parts.append("Esperado: atenção ao cliente/satisfação.")
        rs = float(riscos.get("score") or 0)
        parts.append(f"Risco previsto (heurístico): {cls.risk_level_from_score(rs)} (score={rs:.2f}).")
        if not parts:
            parts.append(f"Ação {action}: execução estável com base no contexto atual.")
        return " ".join(parts)

    @classmethod
    def adjust_confidence(
        cls,
        base_confidence: float,
        *,
        reality: RealityState,
        risco_score: float,
    ) -> float:
        """Reduz confiança sob carga alta ou risco alto."""
        load = float((reality.dynamic_metrics or {}).get("estimated_load") or 0)
        penalty = min(0.35, risco_score * 0.2 + load * 0.15)
        return max(0.05, min(1.0, base_confidence - penalty))

    @classmethod
    def score_decision_quality(
        cls,
        *,
        outcome_atraso: bool,
        predicted_risk_high: bool,
        erro_operacional: bool,
    ) -> Tuple[float, bool]:
        """
        decision_score posterior ∈ [0,1]; was_effective heurístico.
        """
        if erro_operacional:
            return 0.15, False
        if predicted_risk_high and outcome_atraso:
            return 0.55, True
        if not predicted_risk_high and not outcome_atraso:
            return 0.92, True
        if outcome_atraso:
            return 0.45, False
        return 0.75, True

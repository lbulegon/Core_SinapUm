"""
Função objetivo estratégica (otimização explícita, sem LLM).
Compete com múltiplas propostas via score escalar 0–1.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.strategic.strategy_models import KPIBundle, StrategyProposal

# Modos de objetivo (podem combinar-se com pesos)
MAXIMIZE_PROFIT = "maximize_profit"
MINIMIZE_DELAY = "minimize_delay"
BALANCE_LOAD = "balance_load"


class ObjectiveFunction:
    """
    Agrega contribuições de lucro, tempo/fila e equilíbrio carga×margem.
    Usar após simulação (local ou sistémica) para ranquear propostas.
    """

    @classmethod
    def default_weights(cls) -> Dict[str, float]:
        raw = (os.getenv("STRATEGIC_OBJECTIVE_WEIGHTS_JSON") or "").strip()
        if raw:
            try:
                import json

                d = json.loads(raw)
                if isinstance(d, dict):
                    return {str(k): float(v) for k, v in d.items()}
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
        return {
            MAXIMIZE_PROFIT: 0.45,
            MINIMIZE_DELAY: 0.35,
            BALANCE_LOAD: 0.20,
        }

    @classmethod
    def score(
        cls,
        proposal: StrategyProposal,
        *,
        simulation: Optional[Dict[str, Any]] = None,
        kpi: Optional[KPIBundle] = None,
        operational_load: float = 0.0,
        objectives: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> float:
        """
        Retorna score global 0–1 (maior = melhor alinhamento com objetivos).
        `simulation` pode vir de simulate_price_change / systemic / menu_remove.
        """
        sim = simulation or {}
        w = dict(weights or cls.default_weights())
        objs = objectives or list(w.keys())
        # normalizar pesos só sobre objetivos ativos
        active = {o: max(0.0, float(w.get(o, 0))) for o in objs}
        s = sum(active.values())
        if s <= 0:
            active = cls.default_weights()
            s = sum(active.values())
        active = {k: v / s for k, v in active.items()}

        profit_term = cls._profit_term(proposal, sim, kpi)
        delay_term = cls._delay_term(sim, kpi)
        balance_term = cls._balance_term(proposal, sim, operational_load, kpi)

        out = (
            active.get(MAXIMIZE_PROFIT, 0) * profit_term
            + active.get(MINIMIZE_DELAY, 0) * delay_term
            + active.get(BALANCE_LOAD, 0) * balance_term
        )
        return max(0.0, min(1.0, round(out, 4)))

    @staticmethod
    def _profit_term(
        proposal: StrategyProposal,
        sim: Dict[str, Any],
        kpi: Optional[KPIBundle],
    ) -> float:
        # margem_depois ou delta lucro sistémico
        if sim.get("lucro_total_delta_pct") is not None:
            d = float(sim["lucro_total_delta_pct"]) / 100.0
            return max(0.0, min(1.0, 0.5 + d))
        md = sim.get("margem_depois")
        ma = sim.get("margem_antes")
        if md is not None and ma is not None:
            try:
                gain = float(md) - float(ma)
                return max(0.0, min(1.0, 0.5 + gain * 3.0))
            except (TypeError, ValueError):
                pass
        if sim.get("receita_depois") and sim.get("receita_antes"):
            try:
                r0, r1 = float(sim["receita_antes"]), float(sim["receita_depois"])
                if r0 > 0:
                    return max(0.0, min(1.0, 0.45 + 0.55 * (r1 - r0) / r0))
            except (TypeError, ValueError):
                pass
        return 0.35 + 0.25 * float(proposal.impacto_estimado or 0)

    @staticmethod
    def _delay_term(sim: Dict[str, Any], kpi: Optional[KPIBundle]) -> float:
        # menor tempo produção / maior alívio fila = melhor
        if sim.get("fila_alivio_pct") is not None:
            return max(0.0, min(1.0, float(sim["fila_alivio_pct"]) / 25.0))
        t0 = sim.get("tempo_producao_horas", {}).get("antes") if isinstance(sim.get("tempo_producao_horas"), dict) else None
        t1 = sim.get("tempo_producao_horas", {}).get("depois") if isinstance(sim.get("tempo_producao_horas"), dict) else None
        if t0 and t1 and float(t0) > 0:
            reduc = (float(t0) - float(t1)) / float(t0)
            return max(0.0, min(1.0, 0.4 + reduc))
        if kpi and (kpi.custo_atraso_estimado or 0) > 0:
            return 0.55
        return 0.45

    @staticmethod
    def _balance_term(
        proposal: StrategyProposal,
        sim: Dict[str, Any],
        load: float,
        kpi: Optional[KPIBundle],
    ) -> float:
        # penalizar propostas agressivas sob carga extrema; recompensar alívio
        load = max(0.0, min(1.0, float(load)))
        spill = float(sim.get("spillover_stress") or 0)
        score = 0.65 - 0.35 * load - 0.15 * spill
        if proposal.tipo == "preco" and load > 0.82:
            score -= 0.12
        if proposal.tipo == "operacao" and sim.get("fila_alivio_pct"):
            score += 0.1
        if kpi:
            score += 0.08 * float(kpi.eficiencia_operacional or 0)
        return max(0.0, min(1.0, score))


class StrategicProposalEvaluator:
    """
    Alias explícito para auditoria: StrategyEvaluator.score(proposal, …).
    """

    @staticmethod
    def score(
        proposal: StrategyProposal,
        objective_profile: Dict[str, Any],
        *,
        simulation: Optional[Dict[str, Any]] = None,
        kpi: Optional[KPIBundle] = None,
        operational_load: float = 0.0,
    ) -> float:
        objs = objective_profile.get("objectives")
        if not isinstance(objs, list):
            objs = None
        w = objective_profile.get("weights")
        if not isinstance(w, dict):
            w = None
        return ObjectiveFunction.score(
            proposal,
            simulation=simulation,
            kpi=kpi,
            operational_load=operational_load,
            objectives=objs,
            weights=w,
        )

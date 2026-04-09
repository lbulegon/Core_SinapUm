"""
Seleção global entre múltiplas estratégias candidatas (competição + ranking).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from core.services.cognitive_core.strategic.strategy_models import KPIBundle, StrategyProposal
from core.services.cognitive_core.strategic.strategy_objective import StrategicProposalEvaluator


@dataclass
class ScoredStrategy:
    proposal: StrategyProposal
    score: float
    simulation: Dict[str, Any]
    breakdown: Dict[str, Any]


class StrategySelector:
    """
    Gera N propostas → simula → pontua com função objetivo → devolve as melhores.
    """

    @classmethod
    def select_best(
        cls,
        candidates: List[Tuple[StrategyProposal, Dict[str, Any]]],
        *,
        objective_profile: Dict[str, Any],
        kpi: Optional[KPIBundle] = None,
        operational_load: float = 0.0,
        top_k: int = 5,
    ) -> List[ScoredStrategy]:
        scored: List[ScoredStrategy] = []
        for prop, sim in candidates:
            s = StrategicProposalEvaluator.score(
                prop,
                objective_profile,
                simulation=sim,
                kpi=kpi,
                operational_load=operational_load,
            )
            scored.append(
                ScoredStrategy(
                    proposal=prop,
                    score=s,
                    simulation=sim,
                    breakdown={"objective_profile": objective_profile},
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[: max(1, top_k)]

"""
Modelos de dados estratégicos (Fase 4) — acima da operação imediata.
Sem ORM aqui: estruturas puras + persistência via StrategyFeedbackRecord (Django).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class EconomicModel:
    """Visão económica agregada (fonte: MrFoo + parâmetros)."""

    receita: float = 0.0
    custo: float = 0.0
    margem: float = 0.0  # 0–1 ou % conforme contexto
    tempo_producao_medio_min: float = 0.0
    capacidade_operacional: float = 1.0  # 0–1 carga vs capacidade nominal
    periodo_dias: int = 30
    moeda: str = "BRL"
    extra: Dict[str, Any] = field(default_factory=dict)

    def margem_pct(self) -> float:
        if self.receita <= 0:
            return 0.0
        return max(0.0, min(100.0, (1.0 - self.custo / self.receita) * 100.0))


@dataclass
class ProductKPI:
    """KPI por produto / item."""

    item_id: str
    nome: str
    receita: float
    custo_estimado: float
    unidades: float
    margem_pct: float
    tempo_prep_medio_min: float
    lucro_por_hora_prep: float  # proxy: margem / tempo
    score: float = 0.0  # ranking interno


@dataclass
class KPIBundle:
    """Pacote calculado pelo KPIEngine."""

    economic: EconomicModel
    por_produto: List[ProductKPI] = field(default_factory=list)
    margem_media_pct: float = 0.0
    lucro_hora_operacao: float = 0.0
    throughput_financeiro_h: float = 0.0  # receita / hora operacional estimada
    custo_atraso_estimado: float = 0.0  # penalidade × tempo atraso
    eficiencia_operacional: float = 0.0  # 0–1 composto
    raw: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyProposal:
    """Proposta estratégica — ainda não é execução."""

    proposal_id: str
    tipo: str  # preco | cardapio | operacao | expansao
    titulo: str
    descricao: str
    impacto_estimado: float  # 0–1
    risco: str  # low | medium | high
    prioridade: str  # low | normal | high | critical
    parametros: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StrategyFeedback:
    """Comparar previsto vs real (persistido em ORM)."""

    strategy_key: str
    predicted_impact: float
    realized_impact: Optional[float]
    variance: Optional[float]
    notas: str = ""

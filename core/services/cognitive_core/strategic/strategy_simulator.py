"""
Simulação de cenários estratégicos (elasticidade linear simples) — antes de aplicar mudanças.
Não usa LLM.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class SimulationResult:
    cenario: str
    receita_antes: float
    receita_depois: float
    margem_antes: float
    margem_depois: float
    demanda_indice_antes: float
    demanda_indice_depois: float
    tempo_producao_horas_antes: float
    tempo_producao_horas_depois: float
    notas: str
    parametros: Dict[str, Any]


def simulate_price_change(
    *,
    receita_base: float,
    margem_pct_base: float,
    custo_fixo_ratio: float = 0.35,
    price_delta_pct: float = 10.0,
    demand_elasticity: float = -0.6,
) -> SimulationResult:
    """
    Ex.: +10% preço → queda de demanda proporcional à elasticidade (linearizada).
    demand_elasticity negativo: preço sobe → quantidade cai.
    """
    p_mult = 1.0 + price_delta_pct / 100.0
    q_mult = 1.0 + demand_elasticity * (price_delta_pct / 100.0)
    q_mult = max(0.3, min(1.5, q_mult))

    rec_antes = receita_base
    rec_depois = receita_base * p_mult * q_mult

    # margem aproximada: custo variável escala com volume; simplificação
    m_antes = margem_pct_base / 100.0 if margem_pct_base > 1 else margem_pct_base
    custo_rel = (1.0 - m_antes) * receita_base * (1.0 - custo_fixo_ratio) + receita_base * custo_fixo_ratio * (1.0 - m_antes)
    custo_depois = custo_rel * q_mult + receita_base * custo_fixo_ratio * (1.0 - m_antes) * 0.98
    m_depois = (rec_depois - custo_depois) / rec_depois if rec_depois > 0 else 0.0

    tempo_antes = 1.0
    tempo_depois = tempo_antes * q_mult

    return SimulationResult(
        cenario=f"preco_{price_delta_pct:+.1f}%",
        receita_antes=round(rec_antes, 2),
        receita_depois=round(rec_depois, 2),
        margem_antes=round(m_antes, 4),
        margem_depois=round(m_depois, 4),
        demanda_indice_antes=1.0,
        demanda_indice_depois=round(q_mult, 4),
        tempo_producao_horas_antes=round(tempo_antes, 4),
        tempo_producao_horas_depois=round(tempo_depois, 4),
        notas="Simulação linear; calibrar elasticidade por tenant.",
        parametros={
            "price_delta_pct": price_delta_pct,
            "demand_elasticity": demand_elasticity,
            "p_mult": p_mult,
            "q_mult": q_mult,
        },
    )


def simulate_menu_remove(
    *,
    receita_total: float,
    receita_item: float,
    margem_pct: float,
) -> SimulationResult:
    """Remover item: perde receita do item; libera tempo implícito (proxy 5%)."""
    rec_d = receita_total - receita_item
    m = margem_pct / 100.0 if margem_pct > 1 else margem_pct
    return SimulationResult(
        cenario="remover_item",
        receita_antes=round(receita_total, 2),
        receita_depois=round(rec_d, 2),
        margem_antes=round(m, 4),
        margem_depois=round(m * 1.02, 4),
        demanda_indice_antes=1.0,
        demanda_indice_depois=0.97,
        tempo_producao_horas_antes=1.0,
        tempo_producao_horas_depois=0.95,
        notas="Remove receita do item; assume pequeno ganho de foco operacional.",
        parametros={"receita_item": receita_item},
    )


def simulate_systemic_price_focus(
    *,
    receita_total: float,
    item_revenue_share: float,
    margem_pct_base: float,
    price_delta_pct: float,
    demand_elasticity: float,
    spillover_recapture: float = 0.18,
    sibling_queue_stress: float = 0.06,
) -> Dict[str, Any]:
    """
    Ação de preço num produto com participação na receita:
    - efeito local no slice
    - parte da procura perdida migra para outros itens (spillover)
    - stress cruzado na fila (proxy) quando share é alto
    """
    share = max(0.02, min(0.95, float(item_revenue_share)))
    rec_slice = receita_total * share
    local = simulate_price_change(
        receita_base=rec_slice,
        margem_pct_base=margem_pct_base,
        price_delta_pct=price_delta_pct,
        demand_elasticity=demand_elasticity,
    )
    q_drop = max(0.0, 1.0 - local.demanda_indice_depois)
    recaptured = rec_slice * q_drop * spillover_recapture
    others = receita_total * (1.0 - share)
    # outros itens absorvem procura com eficiência parcial
    rec_new = local.receita_depois + others + recaptured * 0.92
    lucro_delta_pct = ((rec_new - receita_total) / receita_total * 100.0) if receita_total > 0 else 0.0
    # fila: alto share + preço → mais stress; spillover alivia um pouco concentração
    fila_alivio = (1.0 - share) * q_drop * 12.0 - share * sibling_queue_stress * abs(price_delta_pct)
    spillover_stress = q_drop * (1.0 - spillover_recapture) * share

    base = simulation_to_dict(local)
    base["systemic"] = True
    base["receita_total_antes"] = round(receita_total, 2)
    base["receita_total_depois"] = round(rec_new, 2)
    base["lucro_total_delta_pct"] = round(lucro_delta_pct, 3)
    base["fila_alivio_pct"] = round(max(-5.0, min(20.0, fila_alivio)), 3)
    base["spillover_stress"] = round(max(0.0, min(1.0, spillover_stress)), 4)
    base["item_revenue_share"] = round(share, 4)
    return base


def simulation_to_dict(sim: SimulationResult) -> Dict[str, Any]:
    return {
        "cenario": sim.cenario,
        "receita_antes": sim.receita_antes,
        "receita_depois": sim.receita_depois,
        "margem_antes": sim.margem_antes,
        "margem_depois": sim.margem_depois,
        "demanda_indice": {
            "antes": sim.demanda_indice_antes,
            "depois": sim.demanda_indice_depois,
        },
        "tempo_producao_horas": {
            "antes": sim.tempo_producao_horas_antes,
            "depois": sim.tempo_producao_horas_depois,
        },
        "notas": sim.notas,
        "parametros": sim.parametros,
    }

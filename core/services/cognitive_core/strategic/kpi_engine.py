"""
KPI Engine — métricas financeiras e operacionais a partir de dados agregados (dict).
Sem LLM; fórmulas determinísticas.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.strategic.strategy_models import (
    EconomicModel,
    KPIBundle,
    ProductKPI,
)


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def compute_product_kpis(rows: List[Dict[str, Any]]) -> List[ProductKPI]:
    """
    rows: cada dict com item_id, nome, receita, custo_estimado, unidades, tempo_prep_medio_min (opcional).
    """
    out: List[ProductKPI] = []
    for r in rows:
        receita = _f(r.get("receita"))
        custo = _f(r.get("custo_estimado"))
        unidades = max(0.01, _f(r.get("unidades"), 1.0))
        tprep = max(0.01, _f(r.get("tempo_prep_medio_min"), 15.0))
        margem_pct = max(0.0, (1.0 - custo / receita) * 100.0) if receita > 0 else 0.0
        # proxy lucro/hora de preparo: (receita - custo) / (tempo em horas) / unidades
        margem_val = receita - custo
        horas_prep = tprep / 60.0
        lph = margem_val / max(0.01, horas_prep * unidades)
        score = margem_pct * 0.006 + min(1.0, lph / max(1.0, float(os.getenv("STRATEGIC_LPH_NORM", "80"))))
        out.append(
            ProductKPI(
                item_id=str(r.get("item_id", "")),
                nome=str(r.get("nome", "")),
                receita=receita,
                custo_estimado=custo,
                unidades=unidades,
                margem_pct=round(margem_pct, 2),
                tempo_prep_medio_min=tprep,
                lucro_por_hora_prep=round(lph, 4),
                score=round(min(1.0, score), 4),
            )
        )
    out.sort(key=lambda p: p.score, reverse=True)
    return out


def compute_economic_totals(por_produto: List[ProductKPI]) -> EconomicModel:
    rec = sum(p.receita for p in por_produto)
    cst = sum(p.custo_estimado for p in por_produto)
    tprep = sum(p.tempo_prep_medio_min * p.unidades for p in por_produto)
    u = sum(p.unidades for p in por_produto) or 1.0
    return EconomicModel(
        receita=rec,
        custo=cst,
        margem=(1.0 - cst / rec) if rec > 0 else 0.0,
        tempo_producao_medio_min=tprep / u,
        capacidade_operacional=0.75,
    )


def compute_kpi_bundle(
    *,
    economic_input: Optional[Dict[str, Any]] = None,
    product_rows: Optional[List[Dict[str, Any]]] = None,
    operational: Optional[Dict[str, Any]] = None,
) -> KPIBundle:
    """
    Monta KPIBundle a partir de dicionários serializáveis (MrFoo ou mocks).
    operational: pode trazer atraso_medio_segundos, horas_operacao_dia, etc.
    """
    product_rows = product_rows or []
    por_p = compute_product_kpis(product_rows)
    econ_in = economic_input or {}
    if por_p:
        em = compute_economic_totals(por_p)
    else:
        em = EconomicModel(
            receita=_f(econ_in.get("receita")),
            custo=_f(econ_in.get("custo")),
            margem=_f(econ_in.get("margem")),
            tempo_producao_medio_min=_f(econ_in.get("tempo_producao_medio_min")),
            capacidade_operacional=_f(econ_in.get("capacidade_operacional"), 1.0),
            periodo_dias=int(econ_in.get("periodo_dias") or 30),
        )

    margem_media = sum(p.margem_pct for p in por_p) / len(por_p) if por_p else em.margem_pct()
    op = operational or {}
    horas_dia = max(0.1, _f(op.get("horas_operacao_dia"), 12.0))
    dias = max(1, int(op.get("periodo_dias") or em.periodo_dias or 30))
    horas_op = horas_dia * dias
    throughput_fin = em.receita / max(0.01, horas_op)
    atraso_s = _f(op.get("atraso_medio_segundos") or op.get("atraso_medio"))
    custo_atraso = (atraso_s / 3600.0) * _f(os.getenv("STRATEGIC_DELAY_COST_PER_HOUR", "15"))

    # eficiência composta: margem normalizada + penalidade carga
    load = _f((op.get("dynamic_metrics") or {}).get("estimated_load"))
    eff = max(0.0, min(1.0, (margem_media / 100.0) * 0.6 + (1.0 - min(1.0, load)) * 0.4))

    return KPIBundle(
        economic=em,
        por_produto=por_p,
        margem_media_pct=round(margem_media, 2),
        lucro_hora_operacao=round((em.receita - em.custo) / max(0.01, horas_op), 4),
        throughput_financeiro_h=round(throughput_fin, 4),
        custo_atraso_estimado=round(custo_atraso, 4),
        eficiencia_operacional=round(eff, 4),
        raw={"operational": op, "economic_input": econ_in},
    )

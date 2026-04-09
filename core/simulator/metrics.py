"""
Métricas de fim de linha, atraso vs SLA e deteção de gargalo por estação.
"""

from __future__ import annotations

from typing import Any, Dict, List, TYPE_CHECKING

if TYPE_CHECKING:
    from core.simulator.pipeline import KitchenPipeline

from core.simulator.stations.base import Station


def detectar_gargalo_por_estacoes(*stations: Station) -> Dict[str, Any]:
    melhor_nome = ""
    maior_ratio = -1.0
    detalhe: List[Dict[str, Any]] = []
    for st in stations:
        ocup = len(st.fila) + len(st.em_producao)
        ratio = ocup / max(1, st.capacidade)
        detalhe.append(
            {
                "estacao": st.nome,
                "fila": len(st.fila),
                "em_producao": len(st.em_producao),
                "capacidade": st.capacidade,
                "ratio_carga": round(ratio, 4),
            }
        )
        if ratio > maior_ratio:
            maior_ratio = ratio
            melhor_nome = st.nome
    return {
        "estacao_critica": melhor_nome,
        "ratio_max": round(maior_ratio, 4),
        "por_estacao": detalhe,
    }


def detectar_gargalo(pipeline: "KitchenPipeline") -> Dict[str, Any]:
    return detectar_gargalo_por_estacoes(
        pipeline.prep,
        pipeline.grill,
        pipeline.assembly,
        pipeline.dispatch,
    )


def calcular_metricas(
    resultados: List[Dict[str, Any]],
    *,
    pipeline: "KitchenPipeline | None" = None,
) -> Dict[str, Any]:
    """
    `resultados`: pedidos que concluíram dispatch (`fim_dispatch` definido).
    """
    if not resultados:
        out: Dict[str, Any] = {
            "n": 0,
            "tempo_medio_ciclo": None,
            "taxa_atraso": 0.0,
            "atrasados": 0,
            "gargalo": detectar_gargalo(pipeline) if pipeline else None,
        }
        return out

    lead_times: List[float] = []
    atrasados = 0
    for p in resultados:
        sla = p.get("sla")
        fim = p.get("fim_dispatch")
        ini = p.get("inicio_prep")
        if fim is not None and ini is not None:
            lead_times.append(float(fim) - float(ini))
        if sla is not None and fim is not None and float(fim) > float(sla):
            atrasados += 1

    tempo_medio = sum(lead_times) / len(lead_times) if lead_times else None
    taxa = atrasados / len(resultados)

    return {
        "n": len(resultados),
        "tempo_medio_ciclo": round(tempo_medio, 3) if tempo_medio is not None else None,
        "taxa_atraso": round(taxa, 4),
        "atrasados": atrasados,
        "gargalo": detectar_gargalo(pipeline) if pipeline else None,
    }

"""
Ordenação das filas por prioridade (Chef Agno / KDS).
"""

from __future__ import annotations

from core.simulator.stations.base import Station


def ordenar_fila(station: Station) -> None:
    station.fila.sort(key=lambda p: float(p.get("prioridade", 0.0)), reverse=True)

"""
Simulador de linha de produção (estações + pipeline + métricas).
Integração opcional com Chef Agno para priorização antes da entrada.
"""

from core.simulator.metrics import calcular_metricas, detectar_gargalo
from core.simulator.pipeline import KitchenPipeline

__all__ = ["KitchenPipeline", "calcular_metricas", "detectar_gargalo"]

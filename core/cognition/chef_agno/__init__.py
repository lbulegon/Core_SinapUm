"""
Chef Agno — motor de decisão operacional (marketplace / pedidos).

Fluxo: evento canônico → regras + scorer → comandos → POST no MrFoo (fila Celery lá).
"""

from core.cognition.chef_agno.engine import processar_evento
from core.cognition.chef_agno.scorer import avaliar
from core.cognition.chef_agno.simulator import (
    dry_run,
    executar_preset,
    executar_todos_presets,
    exportar_para_dataset,
    prever_gargalo,
    simular_sequencia,
)
from core.cognition.chef_agno.trainer import registrar_resultado

__all__ = [
    "processar_evento",
    "avaliar",
    "registrar_resultado",
    "dry_run",
    "prever_gargalo",
    "simular_sequencia",
    "executar_preset",
    "executar_todos_presets",
    "exportar_para_dataset",
]

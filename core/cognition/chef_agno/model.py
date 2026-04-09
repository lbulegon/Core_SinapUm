"""
Modelo de scoring (v1 linear). Substituível depois por ML treinado (mesma interface).
"""

from __future__ import annotations

import os
from typing import Any, Dict

from django.conf import settings


def _f(name: str, default: float) -> float:
    try:
        return float(getattr(settings, name, default))
    except (TypeError, ValueError):
        return default


def calcular_score(features: Dict[str, Any]) -> float:
    """
    Score contínuo — política em `policy.decidir` corta em faixas.
    """
    score = 0.0
    score += float(features.get("num_itens", 0)) * _f("CHEF_AGNO_W_ITENS", 1.5)
    score += float(features.get("num_modificadores", 0)) * _f("CHEF_AGNO_W_MODS", 2.0)
    score += float(features.get("carga_atual", 0.0)) * _f("CHEF_AGNO_W_CARGA", 10.0)

    hora = int(features.get("hora_dia", 12))
    pico_ini = int(getattr(settings, "CHEF_AGNO_HORA_PICO_INI", 19))
    pico_fim = int(getattr(settings, "CHEF_AGNO_HORA_PICO_FIM", 22))
    if pico_ini <= hora < pico_fim:
        score += _f("CHEF_AGNO_BONUS_PICO", 5.0)

    # Valor alto aumenta pressão operacional (leve)
    vt = float(features.get("valor_total", 0.0))
    score += min(15.0, vt / max(1.0, _f("CHEF_AGNO_VALOR_NORMALIZADOR", 50.0)))

    # Gargalo previsto: empurra pedidos mais complexos para faixas mais altas
    lim = _f("CHEF_AGNO_GARGALO_LIMITE", 0.85)
    if float(features.get("carga_prevista", 0.0)) > lim:
        score += float(features.get("num_modificadores", 0)) * _f("CHEF_AGNO_W_GARGALO_MODS", 1.5)

    return float(score)

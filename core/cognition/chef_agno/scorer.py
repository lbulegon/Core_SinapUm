"""
Pipeline: features → modelo → política.
Mantém `calcular_complexidade` como alias da heurística de pedido (compat).
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from core.cognition.chef_agno.features import complexidade_pedido_heuristica, extrair_features
from core.cognition.chef_agno.model import calcular_score
from core.cognition.chef_agno.policy import decidir_com_meta


def calcular_complexidade(pedido: Dict[str, Any]) -> float:
    """Legado — mesma fórmula que antes em `scorer.py`."""
    return complexidade_pedido_heuristica(pedido if isinstance(pedido, dict) else {})


def avaliar(evento: Dict[str, Any]) -> Tuple[str, float, Dict[str, Any]]:
    """
    Retorna (acao, score, features).

    `acao` é o nome do comando canônico (confirmar_pedido, postergar_pedido, ...).
    """
    features = extrair_features(evento)
    score = calcular_score(features)
    acao, _categoria = decidir_com_meta(score)
    return acao, float(score), features

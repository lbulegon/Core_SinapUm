"""
Montagem de comandos a partir do evento — política adaptativa (score) ou legado por env.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from core.cognition.chef_agno.policy import categoria_por_score
from core.cognition.chef_agno.scorer import avaliar, calcular_complexidade
from core.cognition.chef_agno.utils import criar_comando


def _legacy_avaliar_pedido(evento: Dict[str, Any]) -> List[Dict[str, Any]]:
    from core.cognition.chef_agno.features import obter_carga_atual

    pedido = evento.get("pedido") or evento.get("order") or {}
    if not isinstance(pedido, dict):
        pedido = {}

    complexidade = calcular_complexidade(pedido)
    carga = obter_carga_atual(evento)
    comandos: List[Dict[str, Any]] = []

    if carga > 0.8:
        comandos.append(criar_comando("postergar_pedido", evento, {"motivo": "carga_alta", "carga": carga}))
        return comandos
    if complexidade > 8:
        comandos.append(
            criar_comando("rejeitar_pedido", evento, {"motivo": "complexidade_elevada", "score": complexidade})
        )
        return comandos
    comandos.append(criar_comando("confirmar_pedido", evento))
    return comandos


def avaliar_pedido(evento: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Uma lista de comandos (normalmente um) com metadados para KDS / rastreio.

    CHEF_AGNO_POLICY=legacy — ifs fixos (carga / complexidade).
    Caso contrário — modelo adaptativo em `scorer.avaliar`.
    """
    if (os.environ.get("CHEF_AGNO_POLICY") or "").strip().lower() == "legacy":
        return _legacy_avaliar_pedido(evento)

    acao, score, features = avaliar(evento)
    categoria = categoria_por_score(score)

    empresa_id = evento.get("empresa_id") or (evento.get("contexto") or {}).get("empresa_id")

    dados_base: Dict[str, Any] = {
        "chef_agno_score": round(score, 4),
        "chef_agno_categoria": categoria,
        "features_resumo": {
            "num_itens": features.get("num_itens"),
            "carga_atual": round(float(features.get("carga_atual", 0)), 4),
            "num_modificadores": features.get("num_modificadores"),
        },
    }
    if empresa_id is not None:
        dados_base["empresa_id"] = int(empresa_id)

    if acao == "reordenar_fila":
        return [criar_comando("reordenar_fila", evento, dict(dados_base))]

    if acao == "postergar_pedido":
        return [criar_comando("postergar_pedido", evento, {**dados_base, "motivo": "score_medio"})]

    if acao == "rejeitar_pedido":
        return [criar_comando("rejeitar_pedido", evento, {**dados_base, "motivo": "score_critico"})]

    # confirmar_pedido
    return [criar_comando("confirmar_pedido", evento, dados_base)]

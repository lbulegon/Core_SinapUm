"""
Política: score contínuo → ação nominal (comando canônico).
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from django.conf import settings


def _t(name: str, default: float) -> float:
    try:
        return float(getattr(settings, name, default))
    except (TypeError, ValueError):
        return default


def categoria_por_score(score: float) -> str:
    if score < _t("CHEF_AGNO_CAT_BAIXA_MAX", 10.0):
        return "BAIXA_CARGA"
    if score < _t("CHEF_AGNO_CAT_MEDIA_MAX", 20.0):
        return "MEDIA_CARGA"
    if score < _t("CHEF_AGNO_CAT_ALTA_MAX", 30.0):
        return "ALTA_CARGA"
    return "CRITICA"


def decidir(score: float) -> str:
    if score < _t("CHEF_AGNO_LIMITE_CONFIRMAR", 10.0):
        return "confirmar_pedido"
    if score < _t("CHEF_AGNO_LIMITE_POSTERGAR", 20.0):
        return "postergar_pedido"
    if score < _t("CHEF_AGNO_LIMITE_REORDENAR", 30.0):
        return "reordenar_fila"
    return "rejeitar_pedido"


def decidir_com_meta(score: float) -> Tuple[str, str]:
    return decidir(score), categoria_por_score(score)

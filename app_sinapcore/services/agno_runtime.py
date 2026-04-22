from __future__ import annotations

import logging
from typing import Any

from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)


def _get_model(label: str):
    return apps.get_model(label)


def get_pedidos_queryset() -> Any | None:
    label = getattr(settings, "AGNO_PEDIDO_MODEL", "mrfoo.Pedido")
    try:
        Model = _get_model(label)
        return Model.objects.all()
    except Exception as exc:
        logger.warning("AGNO_PEDIDO_MODEL inválido (%s): %s", label, exc)
        return None


def get_produtos_queryset() -> Any | None:
    label = getattr(settings, "AGNO_PRODUTO_MODEL", "mrfoo.ItemCardapio")
    try:
        Model = _get_model(label)
        return Model.objects.all()
    except Exception as exc:
        logger.warning("AGNO_PRODUTO_MODEL inválido (%s): %s", label, exc)
        return None


def get_produto_por_id(product_id: int) -> Any | None:
    qs = get_produtos_queryset()
    if qs is None:
        return None
    try:
        return qs.filter(id=int(product_id)).first()
    except Exception:
        return None


def merge_request_context(request_context: dict[str, Any] | None, pedidos_queryset: Any | None) -> dict[str, Any]:
    from services.agno.operational_context import enrich_operational_context

    base = dict(request_context or {})
    return enrich_operational_context(base, pedidos_queryset)

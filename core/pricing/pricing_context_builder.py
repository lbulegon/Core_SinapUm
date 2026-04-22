from __future__ import annotations

import logging
import os
from decimal import Decimal
from typing import Any

from django.apps import apps
from django.conf import settings
from django.db.models import Sum
from django.utils import timezone

from app_sinapcore.services.agno_runtime import get_pedidos_queryset, get_produto_por_id
from core.pricing.pricing_context import PricingContext
from services.agno.operational_context import enrich_operational_context

logger = logging.getLogger(__name__)


def _float_from_money(val: Any) -> float:
    if val is None:
        return 0.0
    if isinstance(val, Decimal):
        return float(val)
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0


def _pedido_item_label() -> str:
    explicit = (getattr(settings, "AGNO_PEDIDO_ITEM_MODEL", None) or "").strip()
    if explicit:
        return explicit
    ped = getattr(settings, "AGNO_PEDIDO_MODEL", "mrfoo.Pedido")
    app_label = ped.split(".", 1)[0]
    return f"{app_label}.PedidoItem"


def _evento_label() -> str | None:
    raw = (getattr(settings, "AGNO_EVENTO_MODEL", None) or os.environ.get("AGNO_EVENTO_MODEL") or "").strip()
    return raw or None


class PricingContextBuilder:
    """Monta :class:`PricingContext` a partir de modelos configurados (AGNO_*_MODEL)."""

    def build(
        self,
        produto_id: int,
        *,
        canal: str = "app",
        empresa_id: int | None = None,
    ) -> PricingContext:
        produto = get_produto_por_id(int(produto_id))
        if produto is None:
            raise ValueError("produto_nao_encontrado")

        preco_base = self._get_preco_base(produto, empresa_id=empresa_id)
        demanda_base = self._get_demanda_item(int(produto_id), empresa_id=empresa_id)
        tempo = self._get_fator_tempo()
        operacional = self._get_operacional(empresa_id=empresa_id)

        clima = self._get_clima()
        evento = self._get_evento(empresa_id=empresa_id)
        economia = self._get_economia()

        demanda_total = self._clamp(demanda_base + clima + evento + economia, 0.0, 1.0)

        metadata = {
            "demanda_item_normalizada": demanda_base,
            "clima": clima,
            "evento": evento,
            "economia": economia,
            "demanda_agregada_pre_clamp": demanda_base + clima + evento + economia,
            "demanda_usada_no_contexto": demanda_total,
        }

        return PricingContext(
            produto_id=int(produto_id),
            preco_base=preco_base,
            demanda=demanda_total,
            tempo=tempo,
            operacional=operacional,
            empresa_id=empresa_id,
            canal=canal,
            timestamp=timezone.now(),
            metadata=metadata,
        )

    def _get_preco_base(self, produto: Any, *, empresa_id: int | None) -> float:
        if empresa_id is not None:
            ft = getattr(produto, "ficha_tecnica", None)
            emp = getattr(ft, "empresa_id", None) if ft is not None else None
            if emp is not None and int(emp) != int(empresa_id):
                raise ValueError("ItemCardapio não pertence à empresa indicada.")

        for attr in ("preco_atual", "preco_venda", "preco"):
            raw = getattr(produto, attr, None)
            if raw is not None:
                return _float_from_money(raw)
        return 0.0

    def _get_demanda_item(self, produto_id: int, *, empresa_id: int | None) -> float:
        label = _pedido_item_label()
        try:
            PedidoItem = apps.get_model(label)
        except Exception as exc:
            logger.debug("PedidoItem indisponível (%s): %s", label, exc)
            return self._demanda_fallback(empresa_id=empresa_id)

        pedido_path = None
        for candidate in ("pedido", "order", "ordem"):
            if hasattr(PedidoItem, candidate):
                pedido_path = candidate
                break
        if not pedido_path:
            return self._demanda_fallback(empresa_id=empresa_id)

        fk_filter: dict[str, Any] = {}
        for name in ("item_cardapio_id", "item_cardapio", "produto_id", "item_id"):
            if not hasattr(PedidoItem, name):
                continue
            if name.endswith("_id"):
                fk_filter[name] = int(produto_id)
            else:
                fk_filter[f"{name}_id"] = int(produto_id)
            break
        if not fk_filter:
            return self._demanda_fallback(empresa_id=empresa_id)

        inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        qs = PedidoItem.objects.filter(**fk_filter)

        pedido_field = PedidoItem._meta.get_field(pedido_path)
        PedidoModel = pedido_field.related_model
        dt_field = "data_pedido" if hasattr(PedidoModel, "data_pedido") else (
            "created_at" if hasattr(PedidoModel, "created_at") else None
        )
        if dt_field:
            qs = qs.filter(**{f"{pedido_path}__{dt_field}__gte": inicio})

        cancel = getattr(PedidoModel, "STATUS_CANCELADO", None)
        if cancel is not None and hasattr(PedidoModel, "status"):
            qs = qs.exclude(**{f"{pedido_path}__status": cancel})

        if empresa_id is not None and hasattr(PedidoModel, "empresa_id"):
            qs = qs.filter(**{f"{pedido_path}__empresa_id": empresa_id})

        agg = qs.aggregate(total=Sum("quantidade"))
        units = float(agg.get("total") or 0)
        ref = float(getattr(settings, "PRICING_BUILDER_DEMAND_REF_UNITS", 50))
        ref = max(ref, 1.0)
        return min(1.0, units / ref)

    def _demanda_fallback(self, *, empresa_id: int | None) -> float:
        pedidos_qs = get_pedidos_queryset()
        if pedidos_qs is None:
            return 0.0
        Model = pedidos_qs.model
        inicio = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        qs = pedidos_qs
        if hasattr(Model, "data_pedido"):
            qs = qs.filter(data_pedido__gte=inicio)
        cancel = getattr(Model, "STATUS_CANCELADO", None)
        if cancel is not None:
            qs = qs.exclude(status=cancel)
        if empresa_id is not None and hasattr(Model, "empresa_id"):
            qs = qs.filter(empresa_id=empresa_id)
        n = qs.count()
        ref = float(getattr(settings, "PRICING_BUILDER_DEMAND_REF_UNITS", 50))
        ref = max(ref, 1.0)
        return min(1.0, float(n) / ref)

    def _get_fator_tempo(self) -> float:
        hora = timezone.localtime().hour
        if 18 <= hora <= 22:
            return 0.3
        if 11 <= hora <= 14:
            return 0.2
        return 0.0

    def _get_operacional(self, *, empresa_id: int | None) -> float:
        pedidos_qs = get_pedidos_queryset()
        if pedidos_qs is None:
            return 0.0
        if empresa_id is not None and hasattr(pedidos_qs.model, "empresa_id"):
            pedidos_qs = pedidos_qs.filter(empresa_id=empresa_id)
        ctx = enrich_operational_context({}, pedidos_qs)
        carga = float(ctx.get("carga_cozinha") or 0)
        ref = float(getattr(settings, "PRICING_BUILDER_OPS_REF_ORDERS", 20))
        ref = max(ref, 1.0)
        return min(1.0, carga / ref)

    def _get_clima(self) -> float:
        try:
            raw = getattr(settings, "PRICING_CLIMA_PLACEHOLDER", None)
            if raw is None or raw == "":
                return 0.0
            return float(raw)
        except (TypeError, ValueError):
            return 0.0

    def _get_evento(self, *, empresa_id: int | None) -> float:
        label = _evento_label()
        if not label:
            return 0.0
        try:
            Evento = apps.get_model(label)
        except Exception as exc:
            logger.debug("Evento indisponível (%s): %s", label, exc)
            return 0.0

        hoje = timezone.localdate()
        qs = Evento.objects.all()
        if hasattr(Evento, "data"):
            qs = qs.filter(data=hoje)
        elif hasattr(Evento, "dia"):
            qs = qs.filter(dia=hoje)
        else:
            return 0.0

        if empresa_id is not None and hasattr(Evento, "empresa_id"):
            qs = qs.filter(empresa_id=empresa_id)

        evento = qs.first()
        if not evento:
            return 0.0

        tipo = getattr(evento, "tipo", None) or getattr(evento, "tipo_evento", "")
        tipo_s = str(tipo).lower()
        if tipo_s in ("alto_fluxo", "alto-fluxo", "high"):
            return 0.3
        if tipo_s in ("medio", "médio", "medium"):
            return 0.15
        return 0.0

    def _get_economia(self) -> float:
        dia = timezone.localtime().day
        if dia <= 10:
            return 0.2
        if dia >= 25:
            return -0.2
        return 0.0

    @staticmethod
    def _clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(max_val, value))

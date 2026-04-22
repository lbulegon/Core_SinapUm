from __future__ import annotations

from collections import defaultdict
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone


class PrevisaoEngine:
    """
    Motor de previsao de demanda por janela recente.
    """

    @staticmethod
    def _iter_itens(pedido: Any):
        itens = getattr(pedido, "itens", None)
        if itens is None:
            return []
        if hasattr(itens, "all"):
            return itens.all()
        if callable(itens):
            return itens()
        return itens

    @staticmethod
    def _get_produto(item: Any):
        return (
            getattr(item, "produto", None)
            or getattr(item, "item_cardapio", None)
            or getattr(item, "item", None)
        )

    @staticmethod
    def _filtrar_janela(pedidos_queryset, inicio):
        if not hasattr(pedidos_queryset, "filter"):
            return pedidos_queryset

        # Compatibilidade com diferentes contratos de data no dominio.
        for field_name in ("criado_em", "created_at", "data_pedido", "data_criacao"):
            try:
                return pedidos_queryset.filter(**{f"{field_name}__gte": inicio})
            except Exception:
                continue
        return pedidos_queryset

    @staticmethod
    def _prever_demanda_core(pedidos_queryset, janela_minutos: int) -> dict[int, float]:
        agora = timezone.now()
        inicio = agora - timedelta(minutes=janela_minutos)

        pedidos = PrevisaoEngine._filtrar_janela(pedidos_queryset, inicio)
        contador: dict[int, float] = defaultdict(float)

        for pedido in pedidos:
            for item in PrevisaoEngine._iter_itens(pedido):
                produto = PrevisaoEngine._get_produto(item)
                if produto is None or getattr(produto, "id", None) is None:
                    continue
                qtd = float(getattr(item, "quantidade", 1) or 1)
                contador[int(produto.id)] += qtd

        return dict(contador)

    @staticmethod
    def prever_demanda(pedidos_queryset, janela_minutos: int = 15, use_cache: bool = True) -> dict[int, float]:
        """
        Analisa historico recente e preve demanda por produto (id -> quantidade).
        """
        if not use_cache:
            return PrevisaoEngine._prever_demanda_core(pedidos_queryset, janela_minutos)

        try:
            from core.services.feature_flags.rollout import is_enabled

            if not is_enabled("AGNO_CACHE_ENABLED", default=True):
                return PrevisaoEngine._prever_demanda_core(pedidos_queryset, janela_minutos)
        except Exception:
            pass

        from .cache_utils import cache_get_or_set, make_cache_key

        def qs_key() -> str:
            try:
                return str(getattr(pedidos_queryset, "query"))
            except Exception:
                return f"id:{id(pedidos_queryset)}"

        ttl = int(getattr(settings, "AGNO_CACHE_TTL_PREVISAO_SEC", 20))
        key = make_cache_key("previsao", [qs_key(), int(janela_minutos)])
        return cache_get_or_set(key, ttl, lambda: PrevisaoEngine._prever_demanda_core(pedidos_queryset, janela_minutos))

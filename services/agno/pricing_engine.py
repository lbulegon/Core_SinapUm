from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from .custo_engine import CustoEngine
from .ppa_engine import PPAEngine
from .previsao_engine import PrevisaoEngine


class PricingEngine:
    """
    Preco dinamico operacional: equilibra custo, demanda prevista, PPA e carga.
    Nao persiste preco; retorna sugestao para API/KDS/Chef Agno.
    """

    @staticmethod
    def _margem_como_decimal(produto: Any) -> Decimal:
        raw = getattr(produto, "margem", None)
        if raw is None:
            raw = getattr(produto, "margem_lucro", None)
        if raw is None:
            return Decimal("0.3")
        try:
            m = Decimal(str(raw))
        except Exception:
            return Decimal("0.3")
        if m > 1:
            return m / Decimal("100")
        if m < 0:
            return Decimal("0.3")
        return m

    @staticmethod
    def _clamp_fator(valor: float, lo: float = 0.7, hi: float = 2.0) -> float:
        return max(lo, min(float(valor), hi))

    @staticmethod
    def calcular_preco_dinamico(
        produto: Any,
        pedidos_queryset: Any,
        contexto: dict[str, Any] | None = None,
    ) -> Decimal:
        custo = CustoEngine.obter_custo_produto(produto)
        if custo is None or custo <= 0:
            fallback = getattr(produto, "preco", 0) or 0
            try:
                return Decimal(str(fallback)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            except Exception:
                return Decimal("0")

        previsao = PrevisaoEngine.prever_demanda(pedidos_queryset)
        pid = getattr(produto, "id", None)
        demanda = float(previsao.get(int(pid), 0.0) if pid is not None else 0.0)

        ppa = float(PPAEngine.calcular_ppa(produto, contexto))

        tempo = float(
            getattr(produto, "tempo_preparo", None)
            or getattr(produto, "tempo_preparo_estimado", 0)
            or 0
        )
        margem_base = PricingEngine._margem_como_decimal(produto)

        carga = 0.0
        if contexto:
            carga = float(contexto.get("carga_cozinha", 0) or 0)

        fator_demanda = PricingEngine._clamp_fator(1.0 + (demanda * 0.05))
        fator_carga = PricingEngine._clamp_fator(1.0 + (carga * 0.03))
        fator_tempo = PricingEngine._clamp_fator(1.0 - (tempo * 0.01), lo=0.5, hi=1.5)
        fator_ppa = PricingEngine._clamp_fator(1.0 + (ppa * 0.02))

        um = Decimal("1")
        preco_base = custo * (um + margem_base)
        mult = (
            Decimal(str(fator_demanda))
            * Decimal(str(fator_carga))
            * Decimal(str(fator_ppa))
            * Decimal(str(fator_tempo))
        )
        preco_dinamico = preco_base * mult
        preco_minimo = custo * Decimal("1.1")
        final = preco_dinamico if preco_dinamico > preco_minimo else preco_minimo
        return final.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

from __future__ import annotations

from typing import Any

from .ppa_engine import PPAEngine


class PedidoAnalysis:
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
    def analisar_pedido(pedido: Any, contexto: dict[str, Any] | None = None) -> dict[str, Any]:
        contexto = contexto or {}
        total_ppa = 0.0
        total_tempo = 0.0
        total_complexidade = 0.0
        detalhes: list[dict[str, Any]] = []

        for item in PedidoAnalysis._iter_itens(pedido):
            # Compatível com diferentes contratos
            produto = getattr(item, "produto", None) or getattr(item, "item_cardapio", None) or getattr(item, "item", None)
            if produto is None:
                continue

            ppa = PPAEngine.calcular_ppa(produto, contexto)
            tempo = float(
                getattr(produto, "tempo_preparo", None)
                or getattr(produto, "tempo_preparo_estimado", 0)
                or 0
            )
            complexidade_raw = getattr(produto, "complexidade", 0) or 0
            if isinstance(complexidade_raw, str):
                mapa = {"baixa": 1.0, "media": 2.0, "alta": 3.0}
                complexidade = mapa.get(complexidade_raw.lower(), 0.0)
            else:
                complexidade = float(complexidade_raw)

            quantidade = float(getattr(item, "quantidade", 1) or 1)

            total_ppa += ppa * quantidade
            total_tempo += tempo * quantidade
            total_complexidade += complexidade * quantidade

            detalhes.append(
                {
                    "produto": getattr(produto, "nome", "N/A"),
                    "ppa": ppa,
                    "tempo": tempo,
                    "complexidade": complexidade,
                    "quantidade": quantidade,
                }
            )

        return {
            "pedido_id": getattr(pedido, "id", None),
            "ppa_total": total_ppa,
            "tempo_total": total_tempo,
            "complexidade_total": total_complexidade,
            "itens": detalhes,
        }

    @staticmethod
    def calcular_impacto_operacional(pedido: Any) -> float:
        analise = PedidoAnalysis.analisar_pedido(pedido)
        return analise["tempo_total"] + analise["complexidade_total"] * 2.0

    @staticmethod
    def sugerir_prioridade(pedido: Any, contexto: dict[str, Any] | None = None) -> int:
        analise = PedidoAnalysis.analisar_pedido(pedido, contexto=contexto)
        score = (analise["ppa_total"] * 1.5) - (analise["tempo_total"] * 0.5) - (analise["complexidade_total"] * 0.8)
        if score >= 50:
            return 3
        if score >= 20:
            return 2
        return 1

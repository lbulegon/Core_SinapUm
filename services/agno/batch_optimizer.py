from __future__ import annotations

from collections import defaultdict
from typing import Any

from .ppa_engine import PPAEngine


class BatchOptimizer:
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
    def gerar_batches(pedidos) -> dict[int, list[dict[str, Any]]]:
        """
        Agrupa itens de mesmo produto entre pedidos.
        """
        agrupamento: dict[int, list[dict[str, Any]]] = defaultdict(list)

        for pedido in pedidos:
            for item in BatchOptimizer._iter_itens(pedido):
                produto = BatchOptimizer._get_produto(item)
                if produto is None or getattr(produto, "id", None) is None:
                    continue

                quantidade = float(getattr(item, "quantidade", 1) or 1)
                agrupamento[int(produto.id)].append(
                    {
                        "pedido_id": getattr(pedido, "id", None),
                        "produto": produto,
                        "quantidade": quantidade,
                    }
                )

        return dict(agrupamento)

    @staticmethod
    def calcular_prioridade_batch(qtd: float, ppa: float, tempo: float) -> float:
        return (qtd * 2.0) + (ppa * 1.5) - (tempo * 0.5)

    @staticmethod
    def gerar_batches_inteligentes(pedidos, contexto: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Gera batches enriquecidos com PPA e prioridade operacional.
        """
        contexto = contexto or {}
        raw_batches = BatchOptimizer.gerar_batches(pedidos)
        resultado: list[dict[str, Any]] = []

        for produto_id, itens in raw_batches.items():
            if not itens:
                continue
            produto = itens[0]["produto"]
            total_qtd = sum(float(i.get("quantidade", 0) or 0) for i in itens)

            try:
                ppa = float(PPAEngine.calcular_ppa(produto, contexto))
            except Exception:
                ppa = 0.0

            tempo = float(
                getattr(produto, "tempo_preparo", None)
                or getattr(produto, "tempo_preparo_estimado", 0)
                or 0
            )

            prioridade = BatchOptimizer.calcular_prioridade_batch(total_qtd, ppa, tempo)
            resultado.append(
                {
                    "produto_id": produto_id,
                    "produto": getattr(produto, "nome", f"produto_{produto_id}"),
                    "quantidade_total": total_qtd,
                    "pedidos": [i.get("pedido_id") for i in itens if i.get("pedido_id") is not None],
                    "ppa": ppa,
                    "tempo_preparo": tempo,
                    "prioridade_batch": prioridade,
                }
            )

        return sorted(resultado, key=lambda x: x["prioridade_batch"], reverse=True)

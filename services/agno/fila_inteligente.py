from __future__ import annotations

from typing import Any

from .batch_optimizer import BatchOptimizer
from .pedido_analysis import PedidoAnalysis


class FilaInteligente:
    @staticmethod
    def calcular_score(analise: dict[str, Any]) -> float:
        return (
            (float(analise.get("ppa_total", 0)) * 1.5)
            - (float(analise.get("tempo_total", 0)) * 0.5)
            - (float(analise.get("complexidade_total", 0)) * 0.8)
        )

    @staticmethod
    def ordenar_pedidos(pedidos, contexto: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Ordena sem alterar persistência de pedidos (somente leitura).
        Fail-safe: pedido com erro vai para o fim.
        """
        contexto = contexto or {}
        resultado: list[dict[str, Any]] = []

        for pedido in pedidos:
            try:
                analise = PedidoAnalysis.analisar_pedido(pedido, contexto=contexto)
                score = FilaInteligente.calcular_score(analise)
                resultado.append({"pedido": pedido, "score": score, "analise": analise})
            except Exception as exc:
                resultado.append(
                    {
                        "pedido": pedido,
                        "score": -999.0,
                        "analise": {"pedido_id": getattr(pedido, "id", None), "erro": str(exc)},
                    }
                )

        return sorted(resultado, key=lambda x: x["score"], reverse=True)

    @staticmethod
    def gerar_plano_operacional(pedidos, contexto: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Retorna pacote único para KDS/API:
        - fila priorizada por score
        - batches inteligentes sugeridos
        """
        contexto = contexto or {}
        pedidos_lista = list(pedidos) if not isinstance(pedidos, list) else pedidos
        fila = FilaInteligente.ordenar_pedidos(pedidos_lista, contexto=contexto)
        batches = BatchOptimizer.gerar_batches_inteligentes(pedidos_lista, contexto=contexto)

        return {
            "contexto": contexto,
            "total_pedidos": len(pedidos_lista),
            "fila_priorizada": fila,
            "batches_sugeridos": batches,
        }

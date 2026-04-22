from __future__ import annotations

from typing import Any

from .ppa_engine import PPAEngine
from .previsao_engine import PrevisaoEngine


class MenuDinamico:
    @staticmethod
    def _margem(produto: Any) -> float:
        return float(getattr(produto, "margem", 0) or getattr(produto, "margem_lucro", 0) or 0)

    @staticmethod
    def _tempo(produto: Any) -> float:
        return float(
            getattr(produto, "tempo_preparo", None)
            or getattr(produto, "tempo_preparo_estimado", 0)
            or 0
        )

    @staticmethod
    def avaliar_produto(produto: Any, previsao: dict[int, float], contexto: dict[str, Any] | None) -> tuple[float, float]:
        """
        Calcula score estratégico do produto em tempo real.
        """
        contexto = contexto or {}
        demanda_prevista = float(previsao.get(int(getattr(produto, "id", 0) or 0), 0) or 0)
        ppa = float(PPAEngine.calcular_ppa(produto, contexto))
        tempo = MenuDinamico._tempo(produto)
        margem = MenuDinamico._margem(produto)

        score = (ppa * 2.0) + (demanda_prevista * 1.5) + (margem * 1.2) - (tempo * 0.7)
        return score, demanda_prevista

    @staticmethod
    def classificar_produto(score: float) -> str:
        if score > 15:
            return "DESTACAR"
        if score > 8:
            return "NORMAL"
        if score > 3:
            return "REDUZIR"
        return "OCULTAR"

    @staticmethod
    def gerar_estado_cardapio(pedidos_queryset, produtos_queryset, contexto: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """
        Gera estado dinâmico (não persistido) do cardápio.
        """
        previsao = PrevisaoEngine.prever_demanda(pedidos_queryset)
        resultado: list[dict[str, Any]] = []

        for produto in produtos_queryset:
            produto_id = getattr(produto, "id", None)
            if produto_id is None:
                continue

            score, demanda = MenuDinamico.avaliar_produto(produto, previsao, contexto)
            status = MenuDinamico.classificar_produto(score)

            resultado.append(
                {
                    "produto_id": int(produto_id),
                    "produto": getattr(produto, "nome", f"produto_{produto_id}"),
                    "score": score,
                    "demanda_prevista": demanda,
                    "status": status,
                }
            )

        return sorted(resultado, key=lambda x: x["score"], reverse=True)

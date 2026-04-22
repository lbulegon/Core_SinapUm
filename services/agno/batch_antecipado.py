from __future__ import annotations

from typing import Any

from .ppa_predictivo import PPAPreditivo
from .previsao_engine import PrevisaoEngine


class BatchAntecipado:
    @staticmethod
    def gerar_batches_previstos(
        pedidos_queryset,
        produtos_queryset,
        contexto: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Sugere batches preditivos antes da entrada efetiva dos pedidos.
        """
        contexto = contexto or {}
        previsao = PrevisaoEngine.prever_demanda(pedidos_queryset)
        batches: list[dict[str, Any]] = []

        for produto in produtos_queryset:
            produto_id = getattr(produto, "id", None)
            if produto_id is None:
                continue
            demanda_prevista = float(previsao.get(int(produto_id), 0) or 0)
            if demanda_prevista <= 0:
                continue

            ppa_futuro = float(PPAPreditivo.calcular_ppa_futuro(produto, demanda_prevista, contexto=contexto))
            tempo = float(
                getattr(produto, "tempo_preparo", None)
                or getattr(produto, "tempo_preparo_estimado", 0)
                or 0
            )
            prioridade = (demanda_prevista * 2.0) + (ppa_futuro * 1.5) - (tempo * 0.5)

            batches.append(
                {
                    "produto_id": int(produto_id),
                    "produto": getattr(produto, "nome", f"produto_{produto_id}"),
                    "quantidade_sugerida": demanda_prevista,
                    "ppa_futuro": ppa_futuro,
                    "tempo_preparo": tempo,
                    "prioridade": prioridade,
                }
            )

        return sorted(batches, key=lambda x: x["prioridade"], reverse=True)

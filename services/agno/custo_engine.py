from __future__ import annotations

from decimal import Decimal
from typing import Any


class CustoEngine:
    """
    Leitor de custo por produto com fallback seguro.
    Nao altera dominio, apenas observa.
    """

    @staticmethod
    def obter_custo_produto(produto: Any) -> Decimal:
        # Caminho direto, se existir
        custo_direto = getattr(produto, "custo_por_porcao", None)
        if custo_direto is not None:
            try:
                return Decimal(str(custo_direto))
            except Exception:
                return Decimal("0")

        # Fallback via ficha tecnica ativa (estrutura comum no mrfoo)
        fichas_rel = getattr(produto, "fichas_tecnicas", None)
        if fichas_rel is not None and hasattr(fichas_rel, "filter"):
            ficha = fichas_rel.filter(ativo=True).first()
            if ficha and getattr(ficha, "custo_por_porcao", None) is not None:
                try:
                    return Decimal(str(ficha.custo_por_porcao))
                except Exception:
                    return Decimal("0")

        return Decimal("0")

"""
Estação genérica: fila, capacidade, produção simultânea, conclusão por tick de tempo.
"""

from __future__ import annotations

from typing import Any, Dict, List


class Station:
    def __init__(self, nome: str, capacidade: int, duracao_padrao: int = 3):
        self.nome = nome
        self.capacidade = max(1, int(capacidade))
        self.duracao_padrao = max(1, int(duracao_padrao))
        self.em_producao: List[Dict[str, Any]] = []
        self.fila: List[Dict[str, Any]] = []

    def pode_processar(self) -> bool:
        return len(self.em_producao) < self.capacidade

    def adicionar(self, pedido: Dict[str, Any]) -> None:
        self.fila.append(pedido)

    def _duracao(self, pedido: Dict[str, Any]) -> int:
        k = f"duracao_{self.nome}"
        v = pedido.get(k)
        if v is None:
            return self.duracao_padrao
        return max(1, int(v))

    def processar(self, tempo: int) -> List[Dict[str, Any]]:
        """
        1) Liberta slots (pedidos com fim <= tempo).
        2) Puxa da fila até encher capacidade.
        Retorna pedidos que **terminaram** nesta estação neste tick.
        """
        ini = f"inicio_{self.nome}"
        fim = f"fim_{self.nome}"

        finalizados = [p for p in self.em_producao if p.get(fim, 10**9) <= tempo]
        self.em_producao = [p for p in self.em_producao if p not in finalizados]

        while self.pode_processar() and self.fila:
            p = self.fila.pop(0)
            d = self._duracao(p)
            p[ini] = tempo
            p[fim] = tempo + d
            self.em_producao.append(p)

        return finalizados

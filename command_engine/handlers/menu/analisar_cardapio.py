from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from command_engine.base import BaseCommandHandler
from services.orbitals.analise_cardapio import CardapioAnalysisOrbital


class AnalisarCardapioHandler(BaseCommandHandler):
    command_name = "ANALISAR_CARDAPIO"

    def __init__(self) -> None:
        self.orbital = CardapioAnalysisOrbital()

    def execute(self, command: Any, context: dict[str, Any] | None) -> dict[str, Any]:
        payload = getattr(command, "payload", None) or {}
        produtos = payload.get("produtos", [])
        if not isinstance(produtos, list):
            produtos = []

        resultados = [self.orbital.analisar_produto(item or {}) for item in produtos]
        return {
            "command": self.command_name,
            "total_produtos": len(resultados),
            "resultados": resultados,
            "meta": {"source": payload.get("source", "mrfoo")},
        }


def execute_inline(produtos: list[dict[str, Any]], source: str = "mrfoo") -> dict[str, Any]:
    """
    Atalho testável para execução sem ORM/fila.
    Útil para adapters/sdks fora do runtime de comandos pendentes.
    """
    handler = AnalisarCardapioHandler()
    cmd = SimpleNamespace(command=AnalisarCardapioHandler.command_name, payload={"produtos": produtos, "source": source})
    return handler.execute(cmd, context={"mode": "inline"})

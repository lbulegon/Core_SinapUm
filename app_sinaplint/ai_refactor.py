"""
Sugestões heurísticas de refactor (sem LLM) — alinhadas ao framework interno.

Usado pelo `SinapLint` para enriquecer relatórios com próximos passos acionáveis.
"""

from __future__ import annotations

from typing import Any


class SinapAIRefactor:
    """
    Mapeia mensagens de issues (regex/AST/estrutura) para sugestões e exemplos curtos.
    Extensível: adicionar ramos conforme novas regras do SinapLint.
    """

    def suggest(self, issue: dict[str, Any]) -> dict[str, Any]:
        msg = (issue.get("message") or "").lower()
        path = (issue.get("path") or "").lower()

        if "pause_orders" in msg or "pause_orders" in path:
            return {
                "suggestion": "Enfileirar `SinapCoreCommand` e executar via handler registado.",
                "example": (
                    "SinapCoreCommand.objects.create(command='pause_orders', status='pending'); "
                    "depois `CommandExecutionRuntime.execute_pending()`."
                ),
            }

        if "env_state" in msg or "hardcoded" in msg:
            return {
                "suggestion": "Mover condição para módulo PAOR ou emitir comando nomeado.",
                "example": "Orchestrator emite comando; `command_engine` executa o handler.",
            }

        if msg.startswith("file:") or msg.startswith("dir:"):
            return {
                "suggestion": "Restaurar arquivos/pastas obrigatórios do blueprint em Core_SinapUm.",
                "example": "Ver `app_sinaplint/rules/structure_rules.py` (REQUIRED_DIRS / REQUIRED_FILES).",
            }

        if "estrutura" in msg or "missing" in msg:
            return {
                "suggestion": "Alinhar árvore de pastas com a documentação do README.",
                "example": "agent_core/, command_engine/, services/, models/, views/.",
            }

        return {
            "suggestion": "Rever aderência ao framework (handlers + registry, sem ramos no executor).",
            "example": None,
        }

    def suggest_batch(self, issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [{"issue": iss, "ai": self.suggest(iss)} for iss in issues]

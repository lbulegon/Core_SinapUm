"""
Gera um plano de refactor legível a partir das violações de camada.
"""

from __future__ import annotations

from typing import Any


class RefactorPlanner:
    def generate(self, violations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        plan: list[dict[str, Any]] = []
        seen: set[tuple[str, str, str, str]] = set()

        for v in violations:
            key = (
                v.get("from_layer", ""),
                v.get("to_layer", ""),
                v.get("from", ""),
                v.get("to_module", ""),
            )
            if key in seen:
                continue
            seen.add(key)

            fl = v.get("from_layer")
            tl = v.get("to_layer")
            from_f = v.get("from", "")
            to_m = v.get("to_module", "")

            if fl == "domain" and tl in ("application", "presentation", "infrastructure"):
                plan.append(
                    {
                        "priority": "high",
                        "problem": "Domínio a depender de camada externa",
                        "action": "Inverter dependência (port/interface no domínio; implementação fora)",
                        "suggestion": f"Evitar import de `{to_m}` em `{from_f}`; extrair contrato no domínio.",
                    }
                )
            elif fl == "application" and tl == "presentation":
                plan.append(
                    {
                        "priority": "medium",
                        "problem": "Camada de aplicação a aceder à apresentação",
                        "action": "Isolar DTOs e manter serviços independentes de views/serializers",
                        "suggestion": f"Mover lógica ou usar callbacks/eventos em vez de `{to_m}` em `{from_f}`.",
                    }
                )
            elif fl == "domain" and tl == "application":
                plan.append(
                    {
                        "priority": "high",
                        "problem": "Domínio a depender da camada de aplicação",
                        "action": "Ports & adapters: domínio só conhece interfaces",
                        "suggestion": f"Substituir `{to_m}` por abstração definida no domínio.",
                    }
                )
            else:
                plan.append(
                    {
                        "priority": "low",
                        "problem": f"Dependência {fl} → {tl}",
                        "action": "Rever fronteiras de módulo e direção de imports",
                        "suggestion": f"Rever import `{to_m}` em `{from_f}`.",
                    }
                )

        return plan

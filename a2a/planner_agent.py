"""
PlannerAgent — gera plano (steps) a partir de user_input + context.
Fase 2: aceita CognitiveContext + RealityState + DecisionHints (dicts serializáveis) para priorização assistida.
"""
import logging
import re
from typing import Any, Dict, List, Optional

from .schemas import A2APlan, PlanStep

logger = logging.getLogger(__name__)

# Tools conhecidas (existentes no registry) — não inventar
KNOWN_TOOLS = [
    "vitrinezap.analisar_produto",
    "vitrinezap.message.send",
    "vitrinezap.catalog.compose",
    "motopro.slots.allocate",
    "motopro.routes.optimize",
    "mrfoo.menu.generate",
    "mrfoo.shopping_list.generate",
]

# Padrões simples para fallback rule-based (texto → tool + args)
PATTERNS = [
    (r"analis(e|ar)\s+(produto|imagem|foto)", "vitrinezap.analisar_produto", {"intent": "analise_imagem"}),
    (r"cat[áa]logo|listar\s+produtos", "vitrinezap.catalog.compose", {}),
    (r"enviar\s+mensagem|mandar\s+msg", "vitrinezap.message.send", {}),
    (r"alocar\s+vaga|slot|motopro", "motopro.slots.allocate", {}),
    (r"rota|otimizar\s+entrega", "motopro.routes.optimize", {}),
    (r"card[áa]pio|menu\s+mrfoo", "mrfoo.menu.generate", {}),
    (r"lista\s+compras|shopping", "mrfoo.shopping_list.generate", {}),
]


class PlannerAgent:
    """
    Gera plano A2A a partir de user_input e context.
    Sem LLM: usa fallback rule-based (padrões conhecidos → 1 step; senão step noop/prompt).
    """

    def __init__(self, known_tools: Optional[List[str]] = None):
        self.known_tools = known_tools or KNOWN_TOOLS

    def plan(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        constraints: Optional[List[str]] = None,
        *,
        cognitive_context: Optional[Dict[str, Any]] = None,
        reality_state: Optional[Dict[str, Any]] = None,
        decision_hints: Optional[Dict[str, Any]] = None,
    ) -> A2APlan:
        """
        Entrada: user_input, context, constraints (opcional).
        Fase 2: cognitive_context, reality_state, decision_hints — enriquecem heurísticas sem quebrar o legado.
        Saída: A2APlan (intent + steps).
        """
        context = context or {}
        cognitive_context = cognitive_context or context.get("cognitive_context")
        reality_state = reality_state or context.get("reality_state")
        decision_hints = decision_hints or context.get("decision_hints")
        text = (user_input or "").strip().lower()
        intent = "unknown"
        steps: List[PlanStep] = []

        # Priorização assistida: carga operacional alta → preferir fluxos MrFoo / cozinha
        load = 0.0
        if isinstance(reality_state, dict):
            dm = reality_state.get("dynamic_metrics") or {}
            load = float(dm.get("estimated_load") or 0)
            ol = reality_state.get("operational_live") or {}
            snap = ol.get("client_operational_snapshot") or ol.get("operational_snapshot") or {}
            if isinstance(snap, dict) and int(snap.get("pedidos_ativos_count") or 0) > 15:
                load = max(load, 0.85)
        hint_prio = (decision_hints or {}).get("suggested_tool") if isinstance(decision_hints, dict) else None

        for pattern, tool_name, args in PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                intent = f"matched_{tool_name.replace('.', '_')}"
                steps.append(
                    PlanStep(
                        id="step_1",
                        tool_name=tool_name,
                        tool_version="1.0",
                        args=dict(args, user_input=user_input),
                        timeout_seconds=60,
                    )
                )
                break

        if hint_prio and hint_prio in self.known_tools and not steps:
            intent = "hint_assisted"
            steps.append(
                PlanStep(
                    id="step_1",
                    tool_name=str(hint_prio),
                    tool_version="1.0",
                    args={"user_input": user_input, "decision_hints": decision_hints or {}},
                    timeout_seconds=60,
                )
            )

        if not steps:
            intent = "fallback_safe"
            extra = {
                "reason": "no_matching_pattern",
                "user_input": user_input,
                "cognitive_trace_id": (cognitive_context or {}).get("trace_id"),
                "estimated_load": load,
            }
            steps.append(
                PlanStep(
                    id="step_1",
                    tool_name="noop",
                    tool_version="1.0",
                    args=extra,
                    timeout_seconds=30,
                )
            )

        plan = A2APlan(
            intent=intent,
            steps=steps,
            expected_output={
                "cognitive_assist": True,
                "reality_load": load,
                "has_decision_hints": bool(decision_hints),
            },
        )
        logger.info(
            "PlannerAgent plan: intent=%s steps=%s load=%s",
            intent,
            len(steps),
            load,
        )
        return plan

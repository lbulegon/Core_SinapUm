"""
Insight → proposta de ação estruturada (não executa — o loop chama DecisionEngine + safety).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.autonomy.autonomy_logging import log_autonomy
from core.services.cognitive_core.insights.insight_engine import Insight


@dataclass
class ActionProposal:
    action_key: str
    title: str
    rationale: str
    mcp_tool: str
    mcp_input: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"  # low | normal | high


class ActionGenerator:
    """
    Mapeamento determinístico insight/pattern → uma ou várias ações candidatas.
    `candidates_for_insight` (2.0) gera opções; o loop autónomo simula e escolhe a melhor.
    """

    def from_insights(self, insights: List[Insight]) -> List[ActionProposal]:
        """Legado: uma ação por insight (primeiro candidato)."""
        out: List[ActionProposal] = []
        for ins in insights:
            cands = self.candidates_for_insight(ins)
            if cands:
                out.append(cands[0])
        return out

    def candidates_for_insight(self, ins: Insight) -> List[ActionProposal]:
        """Várias opções por padrão — avaliadas por simulação + ranking estratégico no loop."""
        tid = ins.tenant_id
        cands: List[ActionProposal] = []

        if ins.pattern_key == "feedback_recurring_delay":
            cands.append(
                self._prop(
                    "suggest_prep_parallel",
                    "Paralelizar preparo",
                    "Reduzir fila acumulada.",
                    "core.eoc_enrich",
                    {"text": f"mrfoo:autonomy prep parallel tenant={tid}", "context_hint": {"tenant_id": tid, "autonomy": True}},
                    "high",
                )
            )
            cands.append(
                self._prop(
                    "prioritize_low_prep_items",
                    "Priorizar itens de menor tempo de preparo",
                    "Recuperar fluxo atacando primeiro pedidos mais rápidos.",
                    "core.decision_support",
                    {
                        "text": "kds priorizar itens baixo tempo preparo",
                        "source": "autonomy",
                        "context_hint": {"tenant_id": tid, "autonomy": True, "tactic": "low_prep_first"},
                    },
                    "high",
                )
            )
        elif ins.pattern_key == "operational_bottleneck_kitchen":
            cands.append(
                self._prop(
                    "bump_kitchen_priority",
                    "Reforçar priorização na cozinha",
                    "Gargalo em preparo.",
                    "core.decision_support",
                    {
                        "text": "kds gargalo cozinha — priorizar fila",
                        "source": "autonomy",
                        "context_hint": {"tenant_id": tid, "autonomy": True, "fase": "kds_autonomy"},
                    },
                    "high",
                )
            )
            cands.append(
                self._prop(
                    "prioritize_low_prep_items",
                    "Priorizar pedidos de baixo tempo (desbloquear fila)",
                    "Melhor ação quando há gargalo: itens rápidos primeiro.",
                    "core.decision_support",
                    {
                        "text": "gargalo cozinha — priorizar itens rápidos",
                        "source": "autonomy",
                        "context_hint": {"tenant_id": tid, "autonomy": True, "tactic": "low_prep_first"},
                    },
                    "high",
                )
            )
        elif ins.pattern_key == "operational_high_load":
            cands.append(
                self._prop(
                    "shed_load_alert",
                    "Alertar carga alta",
                    "Mitigar entrada de pedidos.",
                    "core.eoc_enrich",
                    {"text": f"mrfoo:autonomy high load tenant={tid}", "context_hint": {"tenant_id": tid, "autonomy": True}},
                    "normal",
                )
            )
            cands.append(
                self._prop(
                    "throughput_recovery_check",
                    "Verificar bloqueios de throughput",
                    "Segunda linha: diagnóstico de fila.",
                    "core.decision_support",
                    {"text": "high load — throughput check", "source": "autonomy", "context_hint": {"tenant_id": tid}},
                    "normal",
                )
            )
        elif ins.pattern_key == "operational_throughput_drop":
            cands.append(
                self._prop(
                    "throughput_recovery_check",
                    "Recuperação de throughput",
                    "Throughput abaixo do referencial.",
                    "core.decision_support",
                    {"text": "throughput drop — verificar operação", "source": "autonomy", "context_hint": {"tenant_id": tid}},
                    "high",
                )
            )
        elif ins.pattern_key == "feedback_success_streak":
            cands.append(
                self._prop(
                    "maintain_policy",
                    "Manter política atual",
                    "Reforço positivo.",
                    "noop",
                    {"reason": "positive_reinforcement", "tenant_id": tid},
                    "low",
                )
            )
        elif ins.pattern_key == "anomaly_low_decision_score":
            cands.append(
                self._prop(
                    "audit_decision_quality",
                    "Auditoria de qualidade de decisão",
                    "Scores baixos.",
                    "core.rag_query",
                    {
                        "query": f"decision quality tenant {tid} feedback",
                        "k": 5,
                        "id_prefix": "mrfoo.order_feedback:",
                    },
                    "normal",
                )
            )

        if not cands:
            p = self._map_insight_legacy(ins)
            if p:
                cands.append(p)
        return cands

    def _prop(
        self,
        key: str,
        title: str,
        rationale: str,
        tool: str,
        inp: Dict[str, Any],
        priority: str,
    ) -> ActionProposal:
        return ActionProposal(
            action_key=key,
            title=title,
            rationale=rationale,
            mcp_tool=tool,
            mcp_input=inp,
            priority=priority,
        )

    def _map_insight_legacy(self, ins: Insight) -> Optional[ActionProposal]:
        tid = ins.tenant_id
        if ins.pattern_key == "feedback_recurring_delay":
            return ActionProposal(
                action_key="suggest_prep_parallel",
                title="Ativar pré-montagem / paralelização leve",
                rationale="Reduzir atraso acumulado observado nos feedbacks.",
                mcp_tool="core.eoc_enrich",
                mcp_input={
                    "text": f"mrfoo:autonomy prep parallel tenant={tid}",
                    "context_hint": {"tenant_id": tid, "autonomy": True, "goal": "reduce_delay"},
                },
                priority="high",
            )
        if ins.pattern_key == "operational_bottleneck_kitchen":
            return ActionProposal(
                action_key="bump_kitchen_priority",
                title="Reforçar priorização na cozinha",
                rationale="Gargalo em preparo detectado no snapshot operacional.",
                mcp_tool="core.decision_support",
                mcp_input={
                    "text": "kds gargalo cozinha — priorizar fila",
                    "source": "autonomy",
                    "context_hint": {
                        "tenant_id": tid,
                        "autonomy": True,
                        "fase": "kds_autonomy",
                    },
                },
                priority="high",
            )
        if ins.pattern_key == "operational_high_load":
            return ActionProposal(
                action_key="shed_load_alert",
                title="Alertar carga alta e suavizar entrada",
                rationale="Carga estimada acima do limiar — mitigar fila.",
                mcp_tool="core.eoc_enrich",
                mcp_input={
                    "text": f"mrfoo:autonomy high load tenant={tid}",
                    "context_hint": {"tenant_id": tid, "autonomy": True, "load": "high"},
                },
                priority="normal",
            )
        if ins.pattern_key == "operational_throughput_drop":
            return ActionProposal(
                action_key="throughput_recovery_check",
                title="Verificar throughput e possíveis bloqueios",
                rationale="Throughput abaixo do referencial.",
                mcp_tool="core.decision_support",
                mcp_input={
                    "text": "throughput drop — verificar operação",
                    "source": "autonomy",
                    "context_hint": {"tenant_id": tid, "autonomy": True},
                },
                priority="high",
            )
        if ins.pattern_key == "feedback_success_streak":
            return ActionProposal(
                action_key="maintain_policy",
                title="Manter política atual (reforço positivo)",
                rationale="Sucesso consistente nas decisões recentes.",
                mcp_tool="noop",
                mcp_input={"reason": "positive_reinforcement", "tenant_id": tid},
                priority="low",
            )
        if ins.pattern_key == "anomaly_low_decision_score":
            return ActionProposal(
                action_key="audit_decision_quality",
                title="Auditoria leve da qualidade de decisão",
                rationale="Scores posteriores baixos.",
                mcp_tool="core.rag_query",
                mcp_input={
                    "query": f"decision quality tenant {tid} feedback",
                    "k": 5,
                    "id_prefix": "mrfoo.order_feedback:",
                },
                priority="normal",
            )
        return None

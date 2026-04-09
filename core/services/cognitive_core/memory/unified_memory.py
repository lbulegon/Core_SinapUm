"""
Memória unificada (Fase 2): episódica, semântica (RAG), estrutural (graph), decisão (feedback).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from core.services.learning.decision_log_service import log_decision

logger = logging.getLogger(__name__)


class UnifiedCognitiveMemory:
    """
    Fachada explícita; não duplica vectorstore — delega a RealityStateBuilder + vectorstore_client.
    Persistência de traço de decisão e ligação a DecisionLog / DecisionFeedbackRecord.
    """

    def episodic_recent(self, trace_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Eventos recentes persistidos (DecisionLog) para o mesmo trace/evento."""
        return self.recent_decision_logs(trace_id, limit=limit)

    def semantic_rag_note(self) -> str:
        return "semantic_memory_is_vectorstore_via_RealityState_rag_long_term"

    def structural_graph_note(self) -> str:
        return "structural_memory_is_RealityState_graph_structural"

    def decision_feedback_recent(
        self, tenant_id: str, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Últimos feedbacks de decisão (Fase 2), por tenant."""
        try:
            from app_inbound_events.models import DecisionFeedbackRecord

            qs = (
                DecisionFeedbackRecord.objects.filter(tenant_id=str(tenant_id))
                .order_by("-created_at")[:limit]
            )
            return [
                {
                    "decision_action": r.decision_action,
                    "was_effective": r.was_effective,
                    "decision_score_posterior": r.decision_score_posterior,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in qs
            ]
        except Exception as e:
            logger.warning("decision_feedback_recent: %s", e)
            return []

    def record_decision_trace(
        self,
        *,
        trace_id: str,
        perception_source: str,
        contexto: Dict[str, Any],
        decisao: Dict[str, Any],
        resultado: Dict[str, Any],
        source: str = "cognitive_core",
    ) -> None:
        log_decision(
            event_id=trace_id,
            contexto=contexto,
            decisao=decisao,
            resultado=resultado,
            source=source,
        )

    def recent_decision_logs(self, trace_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Leitura opcional para contexto (curto prazo persistido)."""
        try:
            from app_inbound_events.models import DecisionLog

            qs = DecisionLog.objects.filter(event_id=trace_id).order_by("-recorded_at")[:limit]
            return [
                {
                    "decisao": e.decisao_json,
                    "resultado": e.resultado_json,
                    "recorded_at": e.recorded_at.isoformat() if e.recorded_at else None,
                }
                for e in qs
            ]
        except Exception as e:
            logger.warning("recent_decision_logs: %s", e)
            return []

"""
Camada de contexto cognitivo: substitui dicts soltos por um contentor versionado.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.services.cognitive_core.perception.input import PerceptionInput


@dataclass
class CognitiveContext:
    """
    Estado atual + histórico recente + variáveis operacionais.
    """

    trace_id: str
    current_state: Dict[str, Any] = field(default_factory=dict)
    recent_events: List[Dict[str, Any]] = field(default_factory=list)
    operational_vars: Dict[str, Any] = field(default_factory=dict)
    rag_namespaces: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "v1"

    @classmethod
    def from_perception(
        cls,
        perception: PerceptionInput,
        *,
        extra: Optional[Dict[str, Any]] = None,
    ) -> "CognitiveContext":
        tid = perception.trace_id or perception.metadata.get("event_id") or "unknown-trace"
        op = dict(extra or {})
        op.setdefault("source", perception.source)
        ns = op.pop("rag_namespaces", None)
        rag_ns: List[str] = []
        if isinstance(ns, list):
            rag_ns = [str(x) for x in ns]
        elif isinstance(ns, str) and ns.strip():
            rag_ns = [ns.strip()]
        hint = perception.context_hint()
        if "rag_namespace" in hint and hint["rag_namespace"]:
            rag_ns.append(str(hint["rag_namespace"]))
        return cls(trace_id=str(tid), operational_vars=op, rag_namespaces=list(dict.fromkeys(rag_ns)))

    def add_event(self, kind: str, payload: Dict[str, Any]) -> None:
        self.recent_events.append(
            {
                "kind": kind,
                "at": datetime.now(timezone.utc).isoformat(),
                "payload": payload,
            }
        )
        if len(self.recent_events) > 50:
            self.recent_events = self.recent_events[-50:]

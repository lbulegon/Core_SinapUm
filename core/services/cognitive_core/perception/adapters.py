"""
Adaptadores de percepção: ligam ingressos existentes a PerceptionInput.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from core.services.cognitive_core.perception.input import PerceptionInput
from core.services.cognitive_core.perception.normalize import normalize_perception_payload


def perception_from_inbound_event(ev: Any, *, trace_id: Optional[str] = None) -> PerceptionInput:
    raw = ev.payload_json or {}
    source = str(ev.source or "inbound")
    norm = normalize_perception_payload(source, raw if isinstance(raw, dict) else {})
    return PerceptionInput(
        source=source,
        raw_data=raw if isinstance(raw, dict) else {},
        normalized_data=norm,
        timestamp=ev.received_at or datetime.now(timezone.utc),
        trace_id=trace_id or str(ev.event_id),
        metadata={"event_id": ev.event_id, "inbound_status": ev.status},
    )


def perception_from_mcp_dict(
    data: Dict[str, Any],
    *,
    source: str = "mcp",
    trace_id: Optional[str] = None,
) -> PerceptionInput:
    """MrFoo / outras tools MCP: payload já parcialmente estruturado."""
    raw = dict(data) if isinstance(data, dict) else {}
    norm = normalize_perception_payload(source, raw)
    return PerceptionInput(
        source=source,
        raw_data=raw,
        normalized_data=norm,
        timestamp=datetime.now(timezone.utc),
        trace_id=trace_id,
        metadata={"ingress": "mcp"},
    )

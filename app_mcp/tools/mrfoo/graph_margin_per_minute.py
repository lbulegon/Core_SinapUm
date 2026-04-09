"""Tool mrfoo.graph.margin_per_minute — margem por minuto por timeslot."""
from typing import Any, Dict, Optional

from adapters.mrfoo_adapter import margin_per_minute as adapter_margin


def graph_margin_per_minute(tenant_id: str, timeslot: Optional[str] = None) -> Dict[str, Any]:
    """Retorna métricas de margem por minuto (timeslot opcional)."""
    return adapter_margin(tenant_id, timeslot)

"""Tool mrfoo.graph.combo_suggestions — sugestões de combos por co-ocorrência."""
from typing import Any, Dict, Optional

from adapters.mrfoo_adapter import combo_suggestions as adapter_combos


def graph_combo_suggestions(tenant_id: str, timeslot: Optional[str] = None) -> Dict[str, Any]:
    """Retorna sugestões de combos (timeslot opcional)."""
    return adapter_combos(tenant_id, timeslot)

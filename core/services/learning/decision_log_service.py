"""
Learning — registro de decisões no pipeline Celery (DecisionLog), sem sistema externo.
"""
from typing import Any, Dict, Optional

from django.utils import timezone

from app_inbound_events.models import DecisionLog


def log_decision(
    *,
    event_id: str,
    contexto: Dict[str, Any],
    decisao: Dict[str, Any],
    resultado: Dict[str, Any],
    source: str = "task_queue_flow",
) -> Optional[DecisionLog]:
    try:
        return DecisionLog.objects.create(
            event_id=event_id,
            source=source,
            contexto_json=contexto,
            decisao_json=decisao,
            resultado_json=resultado,
            recorded_at=timezone.now(),
        )
    except Exception:
        # Não quebra o pipeline
        return None

"""
API REST — Mapa de estado ambiental (Redis): estado atual + histórico leve.
"""

from __future__ import annotations

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from services.environmental_state_service import EnvironmentalStateService


@api_view(["GET"])
@permission_classes([AllowAny])
def get_environmental_state(request, estabelecimento_id: int):
    """
    GET /api/v1/environment/<id>/

    Query:
      - history_limit: int (default 20, max 100)
      - patterns: 1 — inclui deteção heurística de sobrecarga recorrente
    """
    try:
        limit = int(request.GET.get("history_limit", "20"))
    except ValueError:
        limit = 20
    limit = max(1, min(limit, 100))

    current = EnvironmentalStateService.get_state(estabelecimento_id)
    history = EnvironmentalStateService.get_history(estabelecimento_id, limit=limit)

    body: dict = {
        "estabelecimento_id": estabelecimento_id,
        "current": current,
        "history": history,
    }

    if request.GET.get("patterns") == "1":
        body["recurring_overload"] = EnvironmentalStateService.detect_recurring_overload(
            estabelecimento_id
        )
        body["ppa_ambiental_live"] = EnvironmentalStateService.suggest_ppa_ambiental_live(
            estabelecimento_id
        )

    return Response(body)

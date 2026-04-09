"""
Painel server-side — Mapa de Estado Ambiental (Redis + orbital environmental_indiciary).
"""

from __future__ import annotations

from django.shortcuts import render

from services.environmental_state_service import EnvironmentalStateService

_DEFAULT_STATE = {
    "score": 0.0,
    "state": "estavel",
    "confidence": 0.0,
    "indicios": {},
}


def environmental_dashboard(request, estabelecimento_id: int = 1):
    raw = EnvironmentalStateService.get_state(estabelecimento_id)
    no_redis_data = raw is None
    state = raw if raw is not None else dict(_DEFAULT_STATE)

    history = EnvironmentalStateService.get_history(estabelecimento_id, limit=30)
    recurring = EnvironmentalStateService.detect_recurring_overload(estabelecimento_id)
    ppa_live = EnvironmentalStateService.suggest_ppa_ambiental_live(estabelecimento_id)

    indicios_rows: list = []
    if isinstance(state.get("indicios"), dict):
        for k, v in state["indicios"].items():
            try:
                fv = float(v)
                pct = max(0.0, min(100.0, fv * 100.0))
                indicios_rows.append((str(k), fv, pct))
            except (TypeError, ValueError):
                indicios_rows.append((str(k), 0.0, 0.0))

    context = {
        "estabelecimento_id": estabelecimento_id,
        "state": state,
        "no_redis_data": no_redis_data,
        "indicios_rows": indicios_rows,
        "history": history,
        "recurring_overload": recurring,
        "ppa_ambiental_live": ppa_live,
    }
    return render(request, "app_sinapum/environmental/dashboard.html", context)

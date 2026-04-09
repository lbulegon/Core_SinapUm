"""
Segundidade forte: agrega estado operacional real (ORM Core + snapshot injetado por MrFoo).
Vectorstore/RAG não entram aqui — apenas métricas e filas observáveis.
"""
from __future__ import annotations

import logging
import os
from datetime import timedelta
from typing import Any, Dict, List, Optional

from django.db.models import Count
from django.utils import timezone

logger = logging.getLogger(__name__)


def _env_bool(name: str, default: bool = False) -> bool:
    v = (os.getenv(name) or "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def fetch_core_local_operational_metrics(*, hours: int = 24) -> Dict[str, Any]:
    """
    Métricas do próprio Core (Django ORM): volume de decisões e eventos recentes.
    Não substitui KPIs de restaurante — complementa observabilidade cognitiva.
    """
    since = timezone.now() - timedelta(hours=hours)
    out: Dict[str, Any] = {
        "source": "core_orm",
        "window_hours": hours,
        "decision_logs_count": 0,
        "inbound_by_status": {},
        "inbound_recent_count": 0,
    }
    try:
        from app_inbound_events.models import DecisionLog, InboundEvent

        out["decision_logs_count"] = DecisionLog.objects.filter(recorded_at__gte=since).count()
        out["inbound_recent_count"] = InboundEvent.objects.filter(received_at__gte=since).count()
        agg = (
            InboundEvent.objects.filter(received_at__gte=since)
            .values("status")
            .annotate(c=Count("id"))
        )
        out["inbound_by_status"] = {row["status"]: row["c"] for row in agg}
    except Exception as e:
        logger.warning("fetch_core_local_operational_metrics: %s", e)
    return out


def merge_operational_hints(
    perception_hint: Dict[str, Any],
    *,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Injeta snapshot vindo do cliente (ex.: MrFoo em context_hint.operational_snapshot)
    e métricas locais do Core quando habilitado.
    """
    merged: Dict[str, Any] = dict(perception_hint or {})
    snap = merged.get("operational_snapshot")
    if isinstance(snap, dict):
        merged["client_operational_snapshot"] = snap
        merged.setdefault("operational_snapshot", snap)
    if _env_bool("COGNITIVE_CORE_INCLUDE_LOCAL_ORM_METRICS", True):
        merged["core_pipeline_metrics"] = fetch_core_local_operational_metrics()
    if tenant_id and "tenant_id" not in merged:
        merged["tenant_id"] = tenant_id
    return merged


def compute_dynamic_metrics(operational_live: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deriva métricas dinâmicas a partir do snapshot unificado (cliente + Core).
    """
    snap = operational_live.get("client_operational_snapshot") or operational_live.get(
        "operational_snapshot"
    )
    metrics: Dict[str, Any] = {
        "estimated_load": 0.0,
        "avg_delay_seconds": None,
        "throughput_per_hour": None,
        "bottleneck_hint": None,
    }
    if not isinstance(snap, dict):
        core_pm = operational_live.get("core_pipeline_metrics") or {}
        pending = sum(
            int((core_pm.get("inbound_by_status") or {}).get(s, 0) or 0)
            for s in ("RECEIVED", "ENQUEUED", "PROCESSING")
        )
        metrics["estimated_load"] = min(1.0, pending / 50.0) if pending else 0.0
        if pending > 20:
            metrics["bottleneck_hint"] = "inbound_pipeline_backlog"
        return metrics

    active = int(snap.get("pedidos_ativos_count") or snap.get("active_orders") or 0)
    fila_prep = int(snap.get("fila_em_preparo") or snap.get("em_preparo_count") or 0)
    fila_conf = int(snap.get("fila_confirmado") or snap.get("confirmado_count") or 0)
    atraso = snap.get("atraso_medio_segundos")
    tpm = snap.get("tempo_medio_preparo_segundos")

    load = active + fila_prep * 1.2 + fila_conf * 0.8
    metrics["estimated_load"] = min(1.0, load / 40.0)
    if isinstance(atraso, (int, float)):
        metrics["avg_delay_seconds"] = float(atraso)
    if isinstance(tpm, (int, float)):
        metrics["throughput_per_hour"] = round(3600.0 / max(float(tpm), 1.0), 4)

    if fila_prep > max(3, fila_conf) and fila_prep >= 4:
        metrics["bottleneck_hint"] = "cozinha_em_preparo"
    elif fila_conf > 6:
        metrics["bottleneck_hint"] = "fila_confirmacao"
    elif isinstance(atraso, (int, float)) and atraso > 900:
        metrics["bottleneck_hint"] = "atraso_elevado"

    return metrics


def build_operational_live_layer(
    base_operational: Dict[str, Any],
    *,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Camada única `operational_live` para RealityState."""
    merged = merge_operational_hints(base_operational, tenant_id=tenant_id)
    dyn = compute_dynamic_metrics(merged)
    merged["dynamic_metrics_derived"] = dyn
    return merged

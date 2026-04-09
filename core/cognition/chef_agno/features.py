"""
Features numéricas/categóricas para o modelo de scoring (entrada treinável).
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict, List


def _pedido_dict(evento: Dict[str, Any]) -> Dict[str, Any]:
    p = evento.get("pedido") or evento.get("order") or {}
    return p if isinstance(p, dict) else {}


def _itens(pedido: Dict[str, Any]) -> List[Dict[str, Any]]:
    raw = pedido.get("itens") or pedido.get("items") or []
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    return []


def _contar_modificadores(itens: List[Dict[str, Any]]) -> int:
    n = 0
    for item in itens:
        mods = item.get("modificadores") or item.get("modifiers") or item.get("options")
        if isinstance(mods, list):
            n += len(mods)
        elif isinstance(mods, dict):
            n += len(mods)
    return n


def _parse_ts(evento: Dict[str, Any]) -> datetime | None:
    for key in ("timestamp", "created_at", "data_pedido"):
        v = evento.get(key)
        if isinstance(v, str) and v.strip():
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                continue
    return None


def extrair_hora(evento: Dict[str, Any]) -> int:
    dt = _parse_ts(evento)
    if dt is not None:
        return int(dt.hour)
    from django.utils import timezone

    return int(timezone.now().hour)


def extrair_dia_semana(evento: Dict[str, Any]) -> int:
    dt = _parse_ts(evento)
    if dt is not None:
        return int(dt.weekday())
    from django.utils import timezone

    return int(timezone.now().weekday())


def mapear_canal(canal: str) -> int:
    c = (canal or "").strip().upper()
    return {
        "IFOOD": 1,
        "RAPPI": 2,
        "UBER_EATS": 3,
        "WHATSAPP": 4,
        "PDV": 5,
    }.get(c, 0)


def obter_tempo_medio_preparo(evento: Dict[str, Any]) -> float:
    ctx = evento.get("contexto") or {}
    v = ctx.get("tempo_medio_preparo_segundos") or ctx.get("tempo_medio_preparo")
    if isinstance(v, (int, float)):
        return float(v)
    snap = evento.get("operational_snapshot") or ctx.get("operational_snapshot")
    if isinstance(snap, dict):
        tpm = snap.get("tempo_medio_preparo_segundos") or snap.get("tempo_medio_preparo_segundos_estimado")
        if isinstance(tpm, (int, float)):
            return float(tpm)
    try:
        return float(os.environ.get("CHEF_AGNO_TEMPO_PREP_PADRAO", "900"))
    except ValueError:
        return 900.0


def obter_carga_prevista(evento: Dict[str, Any]) -> float:
    ctx = evento.get("contexto") or {}
    if "carga_prevista" in ctx:
        try:
            return max(0.0, min(1.0, float(ctx["carga_prevista"])))
        except (TypeError, ValueError):
            pass
    return 0.0


def _estimated_load_from_snapshot(snap: Dict[str, Any]) -> float:
    active = int(snap.get("pedidos_ativos_count") or snap.get("active_orders") or 0)
    fila_prep = int(snap.get("fila_em_preparo") or snap.get("em_preparo_count") or 0)
    fila_conf = int(snap.get("fila_confirmado") or snap.get("confirmado_count") or 0)
    load = active + fila_prep * 1.2 + fila_conf * 0.8
    return max(0.0, min(1.0, load / 40.0))


def carga_operacional_de_snapshot(snap: Dict[str, Any]) -> float:
    """Carga normalizada 0..1 a partir de um snapshot estilo KDS/MrFoo (simulador, dashboards)."""
    if not isinstance(snap, dict):
        return 0.0
    return _estimated_load_from_snapshot(snap)


def obter_carga_atual(evento: Dict[str, Any]) -> float:
    ctx = evento.get("contexto") or {}
    if "carga_operacional" in ctx:
        try:
            return max(0.0, min(1.0, float(ctx["carga_operacional"])))
        except (TypeError, ValueError):
            pass
    snap = evento.get("operational_snapshot") or ctx.get("operational_snapshot")
    if isinstance(snap, dict):
        return _estimated_load_from_snapshot(snap)
    try:
        return max(0.0, min(1.0, float(os.environ.get("CHEF_AGNO_CARGA_PADRAO", "0.4"))))
    except ValueError:
        return 0.4


def extrair_features(evento: Dict[str, Any]) -> Dict[str, Any]:
    pedido = _pedido_dict(evento)
    itens = _itens(pedido)
    origem = evento.get("origem") or {}

    valor = pedido.get("valor_total")
    if valor is None:
        valor = pedido.get("total")
    try:
        valor_total = float(valor) if valor is not None else 0.0
    except (TypeError, ValueError):
        valor_total = 0.0

    return {
        "num_itens": len(itens),
        "num_modificadores": _contar_modificadores(itens),
        "valor_total": valor_total,
        "hora_dia": extrair_hora(evento),
        "dia_semana": extrair_dia_semana(evento),
        "carga_atual": obter_carga_atual(evento),
        "tempo_medio_preparo": obter_tempo_medio_preparo(evento),
        "canal": mapear_canal(str(origem.get("canal") or "")),
        "carga_prevista": obter_carga_prevista(evento),
    }


def complexidade_pedido_heuristica(pedido: Dict[str, Any]) -> float:
    """Compatível com o scorer legado (2 pts/item + mods)."""
    score = 0.0
    for item in _itens(pedido):
        score += 2.0
        mods = item.get("modificadores") or item.get("modifiers") or item.get("options")
        if isinstance(mods, list):
            score += float(len(mods))
        elif isinstance(mods, dict):
            score += float(len(mods))
    return score

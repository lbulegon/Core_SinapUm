"""
Normalização única de payloads heterogéneos (API, WhatsApp, MrFoo, MCP).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def normalize_perception_payload(source: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produz normalized_data mínimo independentemente da origem.
    Não remove campos úteis: copia shallow e sobrescreve chaves canónicas.
    """
    out: Dict[str, Any] = dict(raw) if isinstance(raw, dict) else {}
    text = out.get("text") or out.get("message") or out.get("body") or ""
    out["text"] = str(text).strip()
    out["message"] = out["text"]
    out["user_id"] = str(out.get("user_id") or out.get("from") or out.get("shopper_id") or "")
    out["channel"] = str(out.get("channel") or source or "unknown")
    out["contract_version"] = str(out.get("contract_version") or "v1")
    if "context_hint" not in out or not isinstance(out.get("context_hint"), dict):
        ch = out.get("context_hint")
        out["context_hint"] = ch if isinstance(ch, dict) else {}
    out["_normalized_at"] = datetime.now(timezone.utc).isoformat()
    out["_perception_source"] = source
    return out

"""
Registo de (features, decisão, resultado) para treino futuro — append JSONL.
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from django.conf import settings

_lock = threading.Lock()


def _path_dataset() -> Path:
    base = Path(getattr(settings, "BASE_DIR", Path.cwd()))
    rel = getattr(settings, "CHEF_AGNO_DATASET_PATH", "var/chef_agno_training.jsonl")
    return base / rel


def registrar_resultado(
    evento: Dict[str, Any],
    decisao: str,
    resultado_real: Dict[str, Any],
    *,
    features: Optional[Dict[str, Any]] = None,
    score: Optional[float] = None,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Anexa uma linha JSON ao dataset (idempotência / replay / treino offline).
    `meta` pode incluir fonte (ex.: simulador), ids de cenário, versão do modelo.
    """
    if not getattr(settings, "CHEF_AGNO_TRAINER_ENABLED", True):
        return
    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "features": features,
        "score": score,
        "decisao": decisao,
        "resultado": resultado_real,
        "evento_id": str(
            evento.get("event_id") or evento.get("id") or evento.get("trace_id") or ""
        ),
        "meta": dict(meta or {}),
    }
    path = _path_dataset()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(row, ensure_ascii=False, default=str) + "\n"
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line)

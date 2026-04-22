from __future__ import annotations

import os
from typing import Any

from django.conf import settings


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


class PPAEngine:
    """
    Motor PPA resiliente a dados incompletos.
    Evita acoplamento forte com models especificos.
    """

    @staticmethod
    def _calcular_ppa_core(produto: Any, contexto: dict[str, Any]) -> float:
        peso_margem = _env_float("PPA_PESO_MARGEM", 2.0)
        peso_demanda = _env_float("PPA_PESO_DEMANDA", 1.5)
        peso_tempo = _env_float("PPA_PESO_TEMPO", 0.7)
        peso_complexidade = _env_float("PPA_PESO_COMPLEXIDADE", 1.2)
        peso_carga = _env_float("PPA_PESO_CARGA", 1.0)

        margem = float(getattr(produto, "margem_lucro", 0) or getattr(produto, "margem", 0) or 0)
        demanda = float(getattr(produto, "demanda_media", 0) or 0)
        tempo = float(
            getattr(produto, "tempo_preparo", None)
            or getattr(produto, "tempo_preparo_estimado", 0)
            or 0
        )

        complexidade_raw = getattr(produto, "complexidade", 0) or 0
        if isinstance(complexidade_raw, str):
            mapa = {"baixa": 1.0, "media": 2.0, "alta": 3.0}
            complexidade = mapa.get(complexidade_raw.lower(), 0.0)
        else:
            complexidade = float(complexidade_raw)

        carga_cozinha = float(contexto.get("carga_cozinha", 0) or 0)

        return float(
            (margem * peso_margem)
            + (demanda * peso_demanda)
            - (tempo * peso_tempo)
            - (complexidade * peso_complexidade)
            - (carga_cozinha * peso_carga)
        )

    @staticmethod
    def calcular_ppa(produto: Any, contexto: dict[str, Any] | None = None, use_cache: bool = True) -> float:
        contexto = contexto or {}

        if not use_cache:
            return PPAEngine._calcular_ppa_core(produto, contexto)

        try:
            from core.services.feature_flags.rollout import is_enabled

            if not is_enabled("AGNO_CACHE_ENABLED", default=True):
                return PPAEngine._calcular_ppa_core(produto, contexto)
        except Exception:
            pass

        from .cache_utils import cache_get_or_set, make_cache_key

        pid = getattr(produto, "id", None)
        carga = float(contexto.get("carga_cozinha", 0) or 0)
        ttl = int(getattr(settings, "AGNO_CACHE_TTL_PPA_SEC", 10))
        key = make_cache_key("ppa", [pid, round(carga, 3)])
        return float(cache_get_or_set(key, ttl, lambda: PPAEngine._calcular_ppa_core(produto, contexto)))

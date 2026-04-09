"""
Estado ambiental em tempo real (Redis) + histórico leve + heurísticas simples.

Chaves:
  env_state:{estabelecimento_id}   — JSON atual, TTL configurável
  env_history:{estabelecimento_id} — lista (LPUSH), últimos N snapshots
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from django.conf import settings

from services.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class EnvironmentalStateService:
    """Mapa de estado ambiental — persistência Redis e leituras."""

    @staticmethod
    def _key(estabelecimento_id: str | int) -> str:
        return f"env_state:{estabelecimento_id}"

    @staticmethod
    def _history_key(estabelecimento_id: str | int) -> str:
        return f"env_history:{estabelecimento_id}"

    @staticmethod
    def save_state(estabelecimento_id: str | int, result: Dict[str, Any]) -> bool:
        """
        Grava estado atual + empurra para histórico.

        `result` esperado (orbital environmental_indiciary.run):
          score, state, confidence opcional, indicios opcional
        """
        r = get_redis_client()
        if r is None:
            logger.debug("EnvironmentalStateService.save_state: Redis indisponível")
            return False

        ttl = int(getattr(settings, "REDIS_TTL_ENV_STATE", 300))
        history_max = int(getattr(settings, "ENV_HISTORY_MAX_LEN", 100))

        payload: Dict[str, Any] = {
            "score": result["score"],
            "state": result["state"],
            "confidence": result.get("confidence", 0.0),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "indicios": result.get("indicios", {}),
        }

        try:
            raw = json.dumps(payload, ensure_ascii=False)
            r.set(EnvironmentalStateService._key(estabelecimento_id), raw, ex=ttl)
            r.lpush(EnvironmentalStateService._history_key(estabelecimento_id), raw)
            r.ltrim(EnvironmentalStateService._history_key(estabelecimento_id), 0, history_max - 1)
            return True
        except Exception as exc:
            logger.warning("EnvironmentalStateService.save_state falhou: %s", exc)
            return False

    @staticmethod
    def get_state(estabelecimento_id: str | int) -> Optional[Dict[str, Any]]:
        r = get_redis_client()
        if r is None:
            return None
        try:
            data = r.get(EnvironmentalStateService._key(estabelecimento_id))
            return json.loads(data) if data else None
        except Exception as exc:
            logger.warning("EnvironmentalStateService.get_state falhou: %s", exc)
            return None

    @staticmethod
    def get_history(estabelecimento_id: str | int, limit: int = 20) -> List[Dict[str, Any]]:
        r = get_redis_client()
        if r is None:
            return []
        try:
            items = r.lrange(
                EnvironmentalStateService._history_key(estabelecimento_id),
                0,
                max(0, limit - 1),
            )
            out: List[Dict[str, Any]] = []
            for i in items:
                try:
                    out.append(json.loads(i))
                except json.JSONDecodeError:
                    continue
            return out
        except Exception as exc:
            logger.warning("EnvironmentalStateService.get_history falhou: %s", exc)
            return []

    @staticmethod
    def detect_recurring_overload(
        estabelecimento_id: str | int,
        window: int = 5,
        min_count: int = 3,
    ) -> bool:
        """Heurística: últimos `window` snapshots com >= min_count vezes 'sobrecarga'."""
        hist = EnvironmentalStateService.get_history(estabelecimento_id, limit=window)
        states = [h.get("state") for h in hist[:window]]
        return states.count("sobrecarga") >= min_count

    @staticmethod
    def suggest_ppa_ambiental_live(estabelecimento_id: str | int) -> Optional[float]:
        """
        PPA ambiental a partir do estado vivo em Redis (0.2–0.9), ou None.
        """
        st = EnvironmentalStateService.get_state(estabelecimento_id)
        if not st:
            return None
        score = float(st.get("score") or 0.0)
        if score > 0.8:
            return 0.9
        if score > 0.6:
            return 0.7
        return 0.3

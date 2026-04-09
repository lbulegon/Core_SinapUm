from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)

# Aliases úteis quando a UI envia rótulos legíveis em vez dos nomes internos
EVALUATION_MODE_ALIASES: dict[str, str] = {
    "grand jury senate": "senate",
    "grand_jury_senate": "senate",
    "senate": "senate",
    "grand jury": "grand_jury",
    "grand_jury": "grand_jury",
}


def normalize_architecture_evaluation(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Converte a resposta de /architecture/evaluate (ou do serviço interno)
    no bloco `governanca` injetado no `semantic_context` do Agent Core.

    Não define regras de negócio — só estrutura dados já produzidos pela avaliação.
    """
    scores = raw.get("scores") or {}
    final = scores.get("final_score")
    if final is None:
        summary = raw.get("summary_scores") or {}
        final = summary.get("final_score")

    return {
        "score_arquitetural": final,
        "scores": scores,
        "riscos": list(raw.get("risks") or []),
        "recomendacoes": list(raw.get("recommendations") or []),
        "strengths": list(raw.get("strengths") or []),
        "evaluation_mode": raw.get("evaluation_mode"),
        "status_avaliacao": raw.get("status"),
        "mock": bool(raw.get("mock")),
        "cycle_id": raw.get("cycle_id"),
        "trace_id": raw.get("trace_id"),
        "source": "architecture_intelligence",
    }


class ArchitectureIntelligenceAdapter:
    """
    Ponte entre Agent Core e Architecture Intelligence.

    - Modo interno (padrão): chama `start_architecture_evaluation` no mesmo processo Django
      (sem HTTP, sem latência de rede, sem CSRF).
    - Modo HTTP: POST para `{base_url}/architecture/evaluate` (útil se o Core estiver em outro host).
    """

    def __init__(
        self,
        *,
        use_http: bool = False,
        base_url: str | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        self.use_http = use_http
        self.base_url = (base_url or os.getenv("AGENT_CORE_AI_HTTP_BASE", "")).rstrip("/")
        self.timeout_seconds = timeout_seconds

    def fetch_evaluation(
        self,
        *,
        bundle_path: str,
        evaluation_mode: str = "full_cycle",
        system_name: str = "MrFoo",
        system_type: str = "Orbital",
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        mode_key = evaluation_mode.strip().lower().replace("-", "_")
        evaluation_mode = EVALUATION_MODE_ALIASES.get(mode_key, evaluation_mode)

        if self.use_http:
            return self._fetch_via_http(
                bundle_path=bundle_path,
                evaluation_mode=evaluation_mode,
                system_name=system_name,
                system_type=system_type,
                trace_id=trace_id,
            )
        return self._fetch_via_internal(
            bundle_path=bundle_path,
            evaluation_mode=evaluation_mode,
            system_name=system_name,
            system_type=system_type,
            trace_id=trace_id,
        )

    def _fetch_via_internal(
        self,
        **kwargs: Any,
    ) -> dict[str, Any]:
        from app_architecture_intelligence.services import start_architecture_evaluation

        return start_architecture_evaluation(
            system_name=kwargs["system_name"],
            system_type=kwargs["system_type"],
            bundle_path=kwargs["bundle_path"],
            evaluation_mode=kwargs["evaluation_mode"],
            trace_id=kwargs.get("trace_id"),
        )

    def _fetch_via_http(self, **kwargs: Any) -> dict[str, Any]:
        if not self.base_url:
            logger.warning(
                "ArchitectureIntelligenceAdapter HTTP sem base_url; defina AGENT_CORE_AI_HTTP_BASE"
            )
            return self._fallback_error("base_url não configurado")

        url = f"{self.base_url}/architecture/evaluate"
        try:
            r = requests.post(
                url,
                json={
                    "system_name": kwargs["system_name"],
                    "system_type": kwargs["system_type"],
                    "bundle_path": kwargs["bundle_path"],
                    "evaluation_mode": kwargs["evaluation_mode"],
                },
                timeout=self.timeout_seconds,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as exc:
            logger.exception("Falha HTTP em Architecture Intelligence: %s", exc)
            return self._fallback_error(str(exc))

    @staticmethod
    def _fallback_error(reason: str) -> dict[str, Any]:
        return {
            "status": "error",
            "evaluation_mode": "fallback",
            "mock": True,
            "scores": {"final_score": None},
            "risks": [f"governance_unavailable: {reason}"],
            "recommendations": [],
            "strengths": [],
        }

    def merge_into_semantic_context(
        self,
        base: dict[str, Any],
        evaluation_raw: dict[str, Any],
    ) -> dict[str, Any]:
        """Anexa `governanca` normalizada ao contexto semântico (imutável em relação ao dict original)."""
        merged = {**base, "governanca": normalize_architecture_evaluation(evaluation_raw)}
        # Hints não são regras do Core — só eco para o Planner/auditoria
        gov = merged["governanca"]
        if gov.get("riscos"):
            merged.setdefault("governance_risk_hints", [])
            for r in gov["riscos"][:8]:
                if r not in merged["governance_risk_hints"]:
                    merged["governance_risk_hints"].append(r)
        return merged

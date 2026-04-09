"""
Orbital indiciário ambiental — integração limpa, extensão do pipeline existente.

Potencial prévio de ação (PPA) via indícios estruturados; sem IoT.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.orbital_result import OrbitalResult

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "orbitals.yaml"

_DEFAULT_WEIGHTS: Dict[str, float] = {
    "ruido": 0.2,
    "fumaca": 0.15,
    "cheiro": 0.1,
    "densidade": 0.25,
    "contaminacao_artefato": 0.2,
    "ritmo_operacional": 0.1,
}

_KEY_ALIASES = {
    "ruido": "ruido",
    "ruído": "ruido",
    "fumaca": "fumaca",
    "fumaça": "fumaca",
    "cheiro": "cheiro",
    "densidade": "densidade",
    "contaminacao_artefato": "contaminacao_artefato",
    "ritmo_operacional": "ritmo_operacional",
}


def _load_yaml_section() -> Dict[str, Any]:
    try:
        with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
            full = yaml.safe_load(f) or {}
        return (full.get("orbital_configs") or {}).get("environmental_indiciary") or {}
    except OSError:
        return {}


def _alertas(estado: str) -> List[str]:
    if estado == "estavel":
        return []
    if estado == "atencao":
        return ["indicios_sugerem_atencao_operacional"]
    if estado == "pressao":
        return ["pressao_ambiental_emergente"]
    if estado == "sobrecarga":
        return ["sobrecarga_provavel", "revisar_ritmo_e_carga"]
    return ["colapso_critico_inferido"]


class EnvironmentalIndiciaryOrbital(BaseOrbital):
    """
    Orbital antecipatório: indícios → score → estado (compatível com BaseOrbital.analyze).
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            orbital_id="environmental_indiciary",
            name="Orbital Indiciário Ambiental",
            version="0.2.0",
        )
        self.config: Dict[str, Any] = config if config is not None else _load_yaml_section()
        self.weights: Dict[str, float] = self._weights_from_config()

    def _weights_from_config(self) -> Dict[str, float]:
        proc = self.config.get("processing") or {}
        w = proc.get("weights")
        if isinstance(w, dict) and w:
            out: Dict[str, float] = {}
            for k, v in w.items():
                try:
                    out[str(k)] = float(v)
                except (TypeError, ValueError):
                    continue
            if out:
                return out
        return dict(_DEFAULT_WEIGHTS)

    def _thresholds(self) -> Dict[str, float]:
        th = self.config.get("thresholds")
        if isinstance(th, dict) and th:
            out: Dict[str, float] = {}
            for k in ("atencao", "pressao", "sobrecarga", "colapso"):
                if k in th:
                    try:
                        out[k] = float(th[k])
                    except (TypeError, ValueError):
                        pass
            if len(out) == 4:
                return out
        return {
            "atencao": 0.4,
            "pressao": 0.6,
            "sobrecarga": 0.8,
            "colapso": 0.95,
        }

    def normalize(self, indicios: Dict[str, Any]) -> Dict[str, float]:
        """Restringe a chaves canónicas e intervalo [0, 1]."""
        out: Dict[str, float] = {}
        for k, v in indicios.items():
            nk = _KEY_ALIASES.get(str(k).strip().lower(), str(k).strip().lower())
            if nk not in self.weights:
                continue
            try:
                fv = float(v)
            except (TypeError, ValueError):
                continue
            out[nk] = max(0.0, min(1.0, fv))
        return out

    def calculate_score(self, indicios: Dict[str, Any]) -> float:
        """Soma ponderada apenas sobre chaves presentes (máx. 1.0 se todos em 1.0)."""
        indicios = self.normalize(indicios)
        score = 0.0
        for key, weight in self.weights.items():
            if key in indicios:
                score += indicios[key] * weight
        return max(0.0, min(1.0, score))

    def classify_state(self, score: float) -> str:
        thresholds = self._thresholds()
        if score >= thresholds.get("colapso", 0.95):
            return "colapso"
        if score >= thresholds.get("sobrecarga", 0.8):
            return "sobrecarga"
        if score >= thresholds.get("pressao", 0.6):
            return "pressao"
        if score >= thresholds.get("atencao", 0.4):
            return "atencao"
        return "estavel"

    def run(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Entrada: context com `indicios_ambientais` (dict).
        Sem indícios: None (orbital opcional, compatível com pipeline).
        """
        raw = context.get("indicios_ambientais")
        if not isinstance(raw, dict) or not raw:
            return None
        indicios = self.normalize(raw)
        if not indicios:
            return None
        score = self.calculate_score(indicios)
        state = self.classify_state(score)
        n_canonical = len(self.weights)
        confidence = len(indicios) / n_canonical if n_canonical else 0.0
        confidence = self.clamp_confidence(confidence)
        return {
            "score": score,
            "state": state,
            "confidence": confidence,
            "indicios": indicios,
        }

    def _extract_context(self, payload: Dict) -> Dict[str, Any]:
        indicios = None
        if payload.get("indicios_ambientais"):
            indicios = payload["indicios_ambientais"]
        elif (payload.get("context") or {}).get("indicios_ambientais"):
            indicios = (payload.get("context") or {}).get("indicios_ambientais")
        elif (payload.get("environmental_indiciary") or {}).get("indicios_ambientais"):
            indicios = (payload.get("environmental_indiciary") or {}).get("indicios_ambientais")
        ctx: Dict[str, Any] = {"indicios_ambientais": indicios or {}}
        eid = payload.get("estabelecimento_id")
        if eid is None:
            c = payload.get("context") or {}
            eid = c.get("estabelecimento_id") or c.get("establishment_id")
        if eid is not None:
            ctx["estabelecimento_id"] = eid
        return ctx

    def _maybe_push_redis(self, ran: Dict[str, Any], ctx: Dict[str, Any]) -> None:
        eid = ctx.get("estabelecimento_id")
        if eid is None:
            return
        try:
            from app.integrations.env_state_redis import push_environmental_state

            push_environmental_state(eid, ran)
        except Exception:
            pass

    def analyze(self, payload: Dict) -> OrbitalResult:
        ctx = self._extract_context(payload)
        ran = self.run(ctx)
        if ran is None:
            return OrbitalResult(
                orbital_id=self.orbital_id,
                name=self.name,
                status="placeholder",
                score=None,
                confidence=None,
                rationale=(
                    "Orbital indiciário ambiental: sem `indicios_ambientais` — opcional, sem impacto."
                ),
                top_features=[],
                raw_features={
                    "inputs_expected": ["indicios_ambientais"],
                    "methodology": (self.config.get("methodology") or {}).get("base")
                    or "indiciary_semiosis",
                },
                version=self.version,
            )

        self._maybe_push_redis(ran, ctx)

        score_01 = float(ran["score"])
        estado = str(ran["state"])
        indicios = ran["indicios"]
        score_estabilidade = max(0.0, min(1.0, 1.0 - score_01))
        alertas = _alertas(estado)
        score_100 = self.clamp_score(score_01 * 100.0)
        conf = float(ran["confidence"])

        raw_features: Dict[str, Any] = {
            "estado_ambiental": estado,
            "score_pressao": round(score_01, 4),
            "score_estabilidade": round(score_estabilidade, 4),
            "alertas": alertas,
            "indicios": indicios,
            "model": (self.config.get("processing") or {}).get("model")
            or "weighted_indiciary_inference",
            "integration_passive": (self.config.get("integration") or {}).get("passive", True),
        }

        rationale = (
            f"Indícios ambientais: score={score_01:.2f}, estado={estado}. "
            "Camada antecipatória passiva."
        )
        top_features = [estado, "indiciary_inference"]
        if alertas:
            top_features.extend(alertas[:2])

        return OrbitalResult(
            orbital_id=self.orbital_id,
            name=self.name,
            status="active",
            score=score_100,
            confidence=conf,
            rationale=rationale,
            top_features=top_features,
            raw_features=raw_features,
            version=self.version,
        )

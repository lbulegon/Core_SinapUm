"""
Intenção do sistema (Fase 4+) — objetivos e KPIs de referência para priorizar autonomia.
Não substitui RealityState; orienta ranking e escolha de ações.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# Objetivos suportados (chaves estáveis)
OBJECTIVE_REDUCE_DELAY = "reduzir_atraso"
OBJECTIVE_INCREASE_MARGIN = "aumentar_margem"
OBJECTIVE_MAX_THROUGHPUT = "maximizar_throughput"
OBJECTIVE_MAINTAIN_STABILITY = "manter_estabilidade"

DEFAULT_OBJECTIVES = [
    OBJECTIVE_REDUCE_DELAY,
    OBJECTIVE_MAX_THROUGHPUT,
    OBJECTIVE_MAINTAIN_STABILITY,
]


@dataclass
class StrategicContext:
    """
    O que o operador/gestor quer perseguir neste ciclo (ou por tenant).
    `kpis` são hints opcionais vindos de MrFoo / painel (margem %, tempo médio, eficiência 0–1).
    """

    objetivos: List[str] = field(default_factory=lambda: list(DEFAULT_OBJECTIVES))
    kpis: Dict[str, float] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    tenant_id: str = ""
    version: str = "v1"

    def weight_for(self, objective: str) -> float:
        if self.weights and objective in self.weights:
            return max(0.0, float(self.weights[objective]))
        # pesos por defeito: atraso e throughput ligeiramente acima de margem
        defaults = {
            OBJECTIVE_REDUCE_DELAY: 0.35,
            OBJECTIVE_MAX_THROUGHPUT: 0.30,
            OBJECTIVE_INCREASE_MARGIN: 0.20,
            OBJECTIVE_MAINTAIN_STABILITY: 0.15,
        }
        return defaults.get(objective, 0.1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "objetivos": self.objetivos,
            "kpis": self.kpis,
            "weights": self.weights,
            "tenant_id": self.tenant_id,
            "version": self.version,
        }

    @classmethod
    def from_payload(cls, data: Optional[Dict[str, Any]] = None) -> "StrategicContext":
        data = data or {}
        raw_obj = data.get("objetivos") or data.get("objectives")
        if isinstance(raw_obj, str) and raw_obj.strip():
            objs = [x.strip() for x in raw_obj.split(",") if x.strip()]
        elif isinstance(raw_obj, list):
            objs = [str(x) for x in raw_obj]
        else:
            objs = _objectives_from_env()
        kpis = data.get("kpis") if isinstance(data.get("kpis"), dict) else {}
        w = data.get("weights") if isinstance(data.get("weights"), dict) else _weights_from_env()
        return cls(
            objetivos=objs or list(DEFAULT_OBJECTIVES),
            kpis={str(k): float(v) for k, v in kpis.items() if _is_number(v)},
            weights={str(k): float(v) for k, v in w.items() if _is_number(v)},
            tenant_id=str(data.get("tenant_id") or ""),
        )


def _is_number(v: Any) -> bool:
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False


def _objectives_from_env() -> List[str]:
    raw = (os.getenv("COGNITIVE_STRATEGIC_OBJECTIVES") or "").strip()
    if not raw:
        return list(DEFAULT_OBJECTIVES)
    return [x.strip() for x in raw.split(",") if x.strip()]


def _weights_from_env() -> Dict[str, float]:
    raw = (os.getenv("COGNITIVE_STRATEGIC_WEIGHTS_JSON") or "").strip()
    if not raw:
        return {}
    try:
        d = json.loads(raw)
        return {str(k): float(v) for k, v in d.items()} if isinstance(d, dict) else {}
    except (json.JSONDecodeError, TypeError, ValueError):
        return {}

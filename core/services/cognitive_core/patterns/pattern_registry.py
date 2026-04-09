"""
Registo declarativo de padrões (detector + metadados). Sem ML — regras sobre sinais.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class PatternDefinition:
    """Identificador estável + descrição para memória e UI."""

    key: str
    description: str
    category: str  # failure | success | operational


# Padrões suportados (chaves usadas pelo PatternEngine)
REGISTERED_KEYS: List[str] = [
    "feedback_recurring_delay",
    "feedback_success_streak",
    "operational_high_load",
    "operational_bottleneck_kitchen",
    "operational_throughput_drop",
    "anomaly_low_decision_score",
]


def list_patterns() -> List[PatternDefinition]:
    return [
        PatternDefinition(
            "feedback_recurring_delay",
            "Taxa elevada de outcomes com atraso nos últimos feedbacks",
            "failure",
        ),
        PatternDefinition(
            "feedback_success_streak",
            "Sequência de decisões avaliadas como efetivas",
            "success",
        ),
        PatternDefinition(
            "operational_high_load",
            "Carga operacional estimada acima do limiar",
            "operational",
        ),
        PatternDefinition(
            "operational_bottleneck_kitchen",
            "Gargalo indicado na cozinha / preparo",
            "operational",
        ),
        PatternDefinition(
            "operational_throughput_drop",
            "Queda de throughput estimado vs referência",
            "operational",
        ),
        PatternDefinition(
            "anomaly_low_decision_score",
            "Scores posteriores de decisão consistentemente baixos",
            "failure",
        ),
    ]


def get_pattern(key: str) -> Optional[PatternDefinition]:
    for p in list_patterns():
        if p.key == key:
            return p
    return None

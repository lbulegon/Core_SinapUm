"""
Terceiridade (Interpretante mediado): saída explícita da mediação — não é só texto LLM.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class DecisionOutput:
    """
    Interpretante operacional: ação escolhida, confiança, raciocínio auditável, metadados.
    Fase 2: expected_outcome, risk_level, decision_score (posterior após feedback).
    """

    action: str
    confidence: float
    reasoning: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    response_text: Optional[str] = None
    use_llm_interpretant: bool = False
    cognitive_version: str = "cognitive_core_v2"
    expected_outcome: Optional[str] = None
    risk_level: str = "medium"
    decision_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
            "response_text": self.response_text,
            "use_llm_interpretant": self.use_llm_interpretant,
            "cognitive_version": self.cognitive_version,
            "expected_outcome": self.expected_outcome,
            "risk_level": self.risk_level,
            "decision_score": self.decision_score,
        }

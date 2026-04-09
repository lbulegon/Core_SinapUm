"""
Núcleo cognitivo unificado (camada semiótica operacional sobre o Core existente).

Peirce (operação no código):
- Signo  → PerceptionInput (entrada estruturada)
- Objeto → RealityState (fatos operacionais + retrieval)
- Interpretante → DecisionOutput (mediação explícita; LLM só como interpretante auxiliar)

Compatibilidade: fluxos legados (MCP, Celery, Evora) permanecem; esta camada adiciona um ponto único
de orquestração e nomenclatura correta (enrich vs decide).
"""

from core.services.cognitive_core.orchestration.orchestrator import CognitiveOrchestrator
from core.services.cognitive_core.perception.input import PerceptionInput
from core.services.cognitive_core.reality.state import RealityState
from core.services.cognitive_core.context.cognitive_context import CognitiveContext
from core.services.cognitive_core.mediation.decision_output import DecisionOutput

__all__ = [
    "CognitiveOrchestrator",
    "PerceptionInput",
    "RealityState",
    "CognitiveContext",
    "DecisionOutput",
]

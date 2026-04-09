"""
Segundidade (Objeto): fatos e resistências operacionais reconhecidas pelo Core.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class RealityState:
    """
    Objeto operacional composto:
    - operational: hints de percepção + metadados (compat Fase 1)
    - operational_live: modelo do mundo operacional (Segundidade forte — Fase 2)
    - dynamic_metrics: throughput, atraso, carga (Fase 2)
    - rag_long_term / rag_context: memória semântica pós-ranking (híbrido)
    - graph_structural: WorldGraph / Neo4j (estrutural)
    """

    operational: Dict[str, Any] = field(default_factory=dict)
    operational_live: Dict[str, Any] = field(default_factory=dict)
    dynamic_metrics: Dict[str, Any] = field(default_factory=dict)
    rag_long_term: List[Dict[str, Any]] = field(default_factory=list)
    rag_context: List[Dict[str, Any]] = field(default_factory=list)
    graph_structural: Dict[str, Any] = field(default_factory=dict)
    rag_namespaces: List[str] = field(default_factory=list)
    version: str = "v2"

    def to_llm_context_slice(self) -> Dict[str, Any]:
        """Trecho estruturado para o interpretante LLM (sem decidir sozinho)."""
        return {
            "operational": self.operational,
            "operational_live": self.operational_live,
            "dynamic_metrics": self.dynamic_metrics,
            "rag": self.rag_long_term,
            "rag_context": self.rag_context,
            "graph": self.graph_structural,
            "rag_namespaces": self.rag_namespaces,
        }

"""
Graph Adapter - Interface para grafos de conhecimento.

ADAPTAR: Integrar com WorldGraph (Neo4j) ou pgvector quando disponível.
Por ora, stub para futura integração.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class GraphAdapter(ABC):
    """Interface para operações em grafo de conhecimento"""

    @abstractmethod
    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Executa query Cypher"""
        pass

    @abstractmethod
    def add_node(self, label: str, properties: Dict[str, Any]) -> str:
        """Adiciona nó ao grafo"""
        pass


class StubGraphAdapter(GraphAdapter):
    """Stub - retorna dados vazios"""

    def query(self, cypher: str, params: Optional[Dict[str, Any]] = None) -> List[Dict]:
        return []

    def add_node(self, label: str, properties: Dict[str, Any]) -> str:
        return "stub_node_id"

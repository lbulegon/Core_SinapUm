"""
Base class para estratégias de criativo
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from services.creative_engine_service.contracts import CreativeBrief, CreativeContext


class BaseStrategy(ABC):
    """Classe base para estratégias de criativo"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome da estratégia"""
        pass
    
    @abstractmethod
    def generate_brief(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        performance_history: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """
        Gera brief específico da estratégia
        
        Args:
            product_data: Dados do produto
            context: Contexto de geração
            performance_history: Histórico de performance (opcional)
        
        Returns:
            CreativeBrief com headline, angle, bullets, etc
        """
        pass

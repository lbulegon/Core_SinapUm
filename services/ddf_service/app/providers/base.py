"""
Base Provider - Classe base para todos os providers
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseProvider(ABC):
    """Classe base para todos os providers de IA"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    def execute(self, prompt: str, **kwargs) -> Dict:
        """
        Executa a tarefa no provider
        
        Args:
            prompt: Texto da tarefa
            **kwargs: Parâmetros adicionais específicos do provider
        
        Returns:
            Dict com resultado da execução
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Verifica se o provider está disponível"""
        pass
    
    def validate_input(self, prompt: str) -> bool:
        """Valida entrada antes de processar"""
        return bool(prompt and len(prompt.strip()) > 0)
    
    def get_metadata(self) -> Dict:
        """Retorna metadados do provider"""
        return {
            'name': self.name,
            'config': self.config
        }


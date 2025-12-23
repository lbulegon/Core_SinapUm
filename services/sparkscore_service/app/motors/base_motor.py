"""
Base Motor - Classe base para todos os motores orbitais
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseOrbitalMotor(ABC):
    """Classe base para motores orbitais"""
    
    def __init__(self, orbital_id: int, orbital_name: str):
        self.orbital_id = orbital_id
        self.orbital_name = orbital_name
    
    @abstractmethod
    def process(
        self,
        stimulus: Dict,
        orbital_result: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Processa estímulo usando motor específico do orbital
        
        Args:
            stimulus: Estímulo original
            orbital_result: Resultado da classificação orbital
            context: Contexto adicional
        
        Returns:
            Dict com resultado do processamento
        """
        pass
    
    def get_metadata(self) -> Dict:
        """Retorna metadados do motor"""
        return {
            'orbital_id': self.orbital_id,
            'orbital_name': self.orbital_name,
            'motor_type': self.__class__.__name__
        }


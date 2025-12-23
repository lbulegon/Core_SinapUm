"""
Motor Orbital 1 - Similaridade / Memória Curta
Reconhecimento - "Já vi isso antes"
"""

from typing import Dict, Optional
from app.motors.base_motor import BaseOrbitalMotor


class SimilarityMotor(BaseOrbitalMotor):
    """Motor para reconhecimento por similaridade (Orbital 1)"""
    
    def __init__(self):
        super().__init__(1, "Reconhecimento")
    
    def process(
        self,
        stimulus: Dict,
        orbital_result: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Processa reconhecimento - busca similaridades
        """
        # Calcular score de similaridade
        familiarity = orbital_result.get('sinais_detectados', {}).get(
            'familiaridade_percebida', 0.0
        )
        
        return {
            'action': 'recognize',
            'processing_score': familiarity,
            'similarity_score': familiarity,
            'recommendation': 'Estímulo reconhecido - potencial para desenvolvimento',
            'metadata': self.get_metadata()
        }


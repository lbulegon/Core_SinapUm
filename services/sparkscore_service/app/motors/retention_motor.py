"""
Motor Orbital 5 - Retenção / Repetição
Memória - Fixação Simbólica
"""

from typing import Dict, Optional
from app.motors.base_motor import BaseOrbitalMotor


class RetentionMotor(BaseOrbitalMotor):
    """Motor para retenção e memória (Orbital 5)"""
    
    def __init__(self):
        super().__init__(5, "Memória")
    
    def process(
        self,
        stimulus: Dict,
        orbital_result: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Processa retenção - fixação na memória
        """
        familiarity = orbital_result.get('sinais_detectados', {}).get(
            'familiaridade_percebida', 0.0
        )
        exposure_time = orbital_result.get('sinais_detectados', {}).get(
            'tempo_exposicao', 0.0
        )
        
        retention_score = (familiarity + exposure_time) / 2.0
        
        return {
            'action': 'retain',
            'processing_score': retention_score,
            'retention_score': retention_score,
            'recommendation': 'Estímulo fixado na memória - potencial para repetição',
            'metadata': self.get_metadata()
        }


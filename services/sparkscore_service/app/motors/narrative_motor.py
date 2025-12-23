"""
Motor Orbital 6 - Propagação Narrativa
Efeito Mandela - Reescrita Coletiva
"""

from typing import Dict, Optional
from app.motors.base_motor import BaseOrbitalMotor


class NarrativeMotor(BaseOrbitalMotor):
    """Motor para efeito Mandela e narrativa coletiva (Orbital 6)"""
    
    def __init__(self):
        super().__init__(6, "Efeito Mandela")
    
    def process(
        self,
        stimulus: Dict,
        orbital_result: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Processa efeito Mandela - PPA cristalizado
        """
        # PPA é cristalizado no Orbital 6
        recurrence = orbital_result.get('sinais_detectados', {}).get(
            'recorrencia_coletiva', 0.0
        )
        familiarity = orbital_result.get('sinais_detectados', {}).get(
            'familiaridade_percebida', 0.0
        )
        
        mandela_score = (recurrence + familiarity) / 2.0
        
        return {
            'action': 'crystallize_ppa',
            'processing_score': mandela_score,
            'mandela_score': mandela_score,
            'ppa_status': 'cristalizado',
            'ppa_confidence': mandela_score,  # PPA cristalizado tem confiança máxima
            'recommendation': 'PPA cristalizado - memória coletiva induzida (Efeito Mandela)',
            'narrative_potential': mandela_score,
            'metadata': self.get_metadata()
        }


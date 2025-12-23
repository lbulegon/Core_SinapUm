"""
Motor Orbital 0 - Filtro de Ruído
Estímulo não integrado - Pré-significação
"""

from typing import Dict, Optional
from app.motors.base_motor import BaseOrbitalMotor


class NoiseFilterMotor(BaseOrbitalMotor):
    """Motor para filtrar ruído (Orbital 0)"""
    
    def __init__(self):
        super().__init__(0, "Ruído")
    
    def process(
        self,
        stimulus: Dict,
        orbital_result: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Filtra ruído - descarta ou marca estímulo como não integrado
        """
        # Se estímulo está em ruído, recomendar descarte ou melhoria
        should_discard = orbital_result.get('impacto_no_sparkscore', 0.0) < 0.2
        
        return {
            'action': 'discard' if should_discard else 'improve',
            'processing_score': 0.0 if should_discard else 0.3,
            'recommendation': (
                'Descartar estímulo - muito ruído' if should_discard
                else 'Melhorar familiaridade e coerência simbólica'
            ),
            'metadata': self.get_metadata()
        }


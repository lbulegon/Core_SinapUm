"""
Factory de Motores Orbitais - Cria motores específicos para cada orbital
"""

from typing import Dict
from app.motors.noise_filter_motor import NoiseFilterMotor
from app.motors.similarity_motor import SimilarityMotor
from app.motors.ppa_motor import PPAMotor
from app.motors.coherence_motor import CoherenceMotor
from app.motors.engagement_motor import EngagementMotor
from app.motors.retention_motor import RetentionMotor
from app.motors.narrative_motor import NarrativeMotor


class OrbitalMotorFactory:
    """Factory para criar motores por orbital"""
    
    _motors = {
        0: NoiseFilterMotor,      # Ruído
        1: SimilarityMotor,       # Reconhecimento
        2: PPAMotor,              # Expectativa (PPA nasce)
        3: CoherenceMotor,        # Alinhamento
        4: EngagementMotor,       # Engajamento
        5: RetentionMotor,        # Memória
        6: NarrativeMotor         # Efeito Mandela
    }
    
    def get_motor(self, orbital_id: int):
        """Retorna motor para orbital específico"""
        motor_class = self._motors.get(orbital_id)
        if not motor_class:
            raise ValueError(f"Motor não encontrado para orbital {orbital_id}")
        return motor_class()


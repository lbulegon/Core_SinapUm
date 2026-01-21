"""
Orbital Temporal - Placeholder
"""

from typing import Dict
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.orbital_result import OrbitalResult


class TemporalOrbital(BaseOrbital):
    """
    Orbital Temporal - Placeholder
    Mediria: adequação temporal, timing, sazonalidade, urgência temporal
    """
    
    def __init__(self):
        super().__init__(
            orbital_id="temporal",
            name="Orbital Temporal",
            version="0.1.0"
        )
    
    def analyze(self, payload: Dict) -> OrbitalResult:
        """
        Retorna resultado placeholder
        """
        return OrbitalResult(
            orbital_id=self.orbital_id,
            name=self.name,
            status="placeholder",
            score=None,
            confidence=None,
            rationale=(
                "Orbital Temporal mediria a adequação temporal da peça, incluindo: "
                "timing de publicação (hora do dia, dia da semana), sazonalidade "
                "(adequação a datas comemorativas, estações), urgência temporal "
                "(ofertas limitadas, prazos), e ressonância com ciclos temporais do público. "
                "Implementação futura requer: dados de contexto temporal (timestamp, "
                "fuso horário, calendário), análise de sazonalidade por categoria, "
                "e possivelmente integração com dados históricos de performance por horário."
            ),
            top_features=[],
            raw_features={},
            version=self.version
        )



"""
Registry de orbitais - Carrega e gerencia orbitais disponíveis
"""

import yaml
from typing import Dict, List
from pathlib import Path
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.semiotic_orbital import SemioticOrbital
from app.orbitals.emotional_orbital import EmotionalOrbital
from app.orbitals.cognitive_orbital import CognitiveOrbital
from app.orbitals.narrative_orbital import NarrativeOrbital
from app.orbitals.cultural_orbital import CulturalOrbital
from app.orbitals.ethical_orbital import EthicalOrbital
from app.orbitals.psychoanalytic_orbital import PsychoanalyticOrbital
from app.orbitals.temporal_orbital import TemporalOrbital
from app.orbitals.social_orbital import SocialOrbital


class OrbitalRegistry:
    """
    Registry que carrega e gerencia orbitais
    """
    
    # Mapeamento de IDs para classes
    _orbital_classes: Dict[str, type] = {
        "semiotic": SemioticOrbital,
        "emotional": EmotionalOrbital,
        "cognitive": CognitiveOrbital,
        "narrative": NarrativeOrbital,
        "cultural": CulturalOrbital,
        "ethical": EthicalOrbital,
        "psychoanalytic": PsychoanalyticOrbital,
        "temporal": TemporalOrbital,
        "social": SocialOrbital,
    }
    
    def __init__(self):
        self.config = self._load_config()
        self._orbitals: Dict[str, BaseOrbital] = {}
        self._initialize_orbitals()
    
    def _load_config(self) -> Dict:
        """Carrega configuração de orbitais do YAML"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'orbitals.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _initialize_orbitals(self):
        """Inicializa instâncias de orbitais"""
        orbital_configs = self.config.get('orbital_configs', {})
        
        for orbital_id, orbital_class in self._orbital_classes.items():
            # Verificar se orbital está habilitado na config
            config = orbital_configs.get(orbital_id, {})
            enabled = config.get('enabled', False)
            
            # Criar instância
            orbital_instance = orbital_class()
            self._orbitals[orbital_id] = orbital_instance
    
    def get_active_orbitals(self) -> List[BaseOrbital]:
        """
        Retorna lista de orbitais ativos (enabled: true)
        Ordenado deterministicamente por orbital_id
        """
        orbital_configs = self.config.get('orbital_configs', {})
        active = []
        
        for orbital_id in sorted(self._orbitals.keys()):
            config = orbital_configs.get(orbital_id, {})
            if config.get('enabled', False):
                active.append(self._orbitals[orbital_id])
        
        return active
    
    def get_placeholder_orbitals(self) -> List[BaseOrbital]:
        """
        Retorna lista de orbitais placeholder (enabled: false)
        Ordenado deterministicamente por orbital_id
        """
        orbital_configs = self.config.get('orbital_configs', {})
        placeholders = []
        
        for orbital_id in sorted(self._orbitals.keys()):
            config = orbital_configs.get(orbital_id, {})
            if not config.get('enabled', False):
                placeholders.append(self._orbitals[orbital_id])
        
        return placeholders
    
    def get_all_orbitals(self) -> List[BaseOrbital]:
        """
        Retorna todos os orbitais (ativos + placeholders)
        Ordenado deterministicamente por orbital_id
        """
        return sorted(self._orbitals.values(), key=lambda o: o.orbital_id)
    
    def get_orbital(self, orbital_id: str) -> BaseOrbital:
        """
        Retorna orbital específico por ID
        
        Args:
            orbital_id: ID do orbital
        
        Returns:
            Instância do orbital
        
        Raises:
            ValueError: Se orbital não encontrado
        """
        if orbital_id not in self._orbitals:
            raise ValueError(f"Orbital '{orbital_id}' não encontrado")
        return self._orbitals[orbital_id]


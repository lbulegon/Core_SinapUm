"""
Módulo de Políticas - Gerencia regras, bloqueios e limites
"""

import yaml
from typing import Dict, List, Optional
from pathlib import Path


class PoliciesManager:
    """Gerencia políticas de segurança e limites"""
    
    def __init__(self):
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict:
        """Carrega políticas do arquivo de configuração"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'policies.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def is_category_allowed(self, category: str) -> bool:
        """Verifica se uma categoria está permitida"""
        blocked = self.policies.get('security', {}).get('blocked', [])
        return category not in blocked
    
    def requires_approval(self, category: str) -> bool:
        """Verifica se uma categoria requer aprovação manual"""
        require_approval = self.policies.get('security', {}).get('require_approval', [])
        return category in require_approval
    
    def get_rate_limit(self, category: str) -> int:
        """Obtém limite de requisições por minuto para uma categoria"""
        rate_limits = self.policies.get('limits', {}).get('rate_limits', {})
        return rate_limits.get(category, rate_limits.get('default', 100))
    
    def get_timeout(self, category: str) -> int:
        """Obtém timeout em segundos para uma categoria"""
        timeouts = self.policies.get('limits', {}).get('timeouts', {})
        return timeouts.get(category, timeouts.get('default', 30))
    
    def should_prioritize_quality(self, category: str) -> bool:
        """Verifica se deve priorizar qualidade sobre velocidade"""
        prioritize_quality = self.policies.get('quality', {}).get('prioritize_quality', [])
        return category in prioritize_quality
    
    def should_prioritize_speed(self, category: str) -> bool:
        """Verifica se deve priorizar velocidade sobre qualidade"""
        prioritize_speed = self.policies.get('quality', {}).get('prioritize_speed', [])
        return category in prioritize_speed
    
    def get_category_policies(self, category: str) -> Dict:
        """Obtém todas as políticas de uma categoria"""
        return {
            'allowed': self.is_category_allowed(category),
            'requires_approval': self.requires_approval(category),
            'rate_limit': self.get_rate_limit(category),
            'timeout': self.get_timeout(category),
            'prioritize_quality': self.should_prioritize_quality(category),
            'prioritize_speed': self.should_prioritize_speed(category)
        }


# Instância global
POLICIES = PoliciesManager()


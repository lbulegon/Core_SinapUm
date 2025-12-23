"""
Módulo de Delegação - Roteia tarefas para providers de IA apropriados
"""

import yaml
import os
from typing import Dict, List, Optional
from pathlib import Path
from .policies import POLICIES


class TaskDelegate:
    """Delega tarefas para providers de IA baseado em regras e scores"""
    
    def __init__(self):
        self.providers_config = self._load_providers()
        self.routes_config = self._load_routes()
        self.policies_config = self._load_policies()
    
    def _load_providers(self) -> Dict:
        """Carrega configuração de providers"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'providers.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_routes(self) -> Dict:
        """Carrega configuração de rotas"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'routes.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _load_policies(self) -> Dict:
        """Carrega políticas de segurança"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'policies.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def delegate(self, detection: Dict, context: Optional[Dict] = None) -> Dict:
        """
        Delega tarefa para provider apropriado
        
        Args:
            detection: Resultado do detect (categoria, intenção, etc.)
            context: Contexto adicional (projeto, usuário, preferências)
        
        Returns:
            Dict com provider escolhido, alternativas e metadados
        """
        category = detection.get('category')
        intent = detection.get('intent')
        urgency = detection.get('urgency', 'normal')
        
        # Verificar políticas de segurança
        if not self._check_policies(category):
            raise Exception(f"Categoria '{category}' bloqueada por políticas de segurança")
        
        # Obter lista de providers disponíveis para a categoria
        available_providers = self.providers_config.get(category, [])
        
        if not available_providers:
            raise Exception(f"Nenhum provider disponível para categoria '{category}'")
        
        # Escolher provider baseado em regras
        primary_provider = self._choose_provider(
            category, 
            available_providers, 
            detection, 
            context
        )
        
        # Obter providers de fallback
        fallback_providers = self._get_fallback_providers(category, primary_provider)
        
        return {
            'category': category,
            'intent': intent,
            'primary_provider': primary_provider,
            'fallback_providers': fallback_providers,
            'available_providers': available_providers,
            'urgency': urgency,
            'policies': self._get_category_policies(category)
        }
    
    def _choose_provider(
        self, 
        category: str, 
        available_providers: List[str],
        detection: Dict,
        context: Optional[Dict]
    ) -> str:
        """Escolhe o melhor provider baseado em regras e contexto"""
        
        # Se há preferência no contexto, usar ela
        if context and 'preferred_provider' in context:
            preferred = context['preferred_provider']
            if preferred in available_providers:
                return preferred
        
        # Usar rota padrão se disponível
        default_route = self.routes_config.get('default_routes', {}).get(category)
        if default_route and default_route in available_providers:
            return default_route
        
        # Usar primeiro provider disponível como fallback
        return available_providers[0]
    
    def _get_fallback_providers(self, category: str, primary: str) -> List[str]:
        """Obtém lista de providers de fallback"""
        fallback_routes = self.routes_config.get('fallback_routes', {})
        fallbacks = fallback_routes.get(category, [])
        
        # Remover o provider primário da lista de fallbacks
        return [p for p in fallbacks if p != primary]
    
    def _check_policies(self, category: str) -> bool:
        """Verifica se categoria está permitida pelas políticas"""
        return POLICIES.is_category_allowed(category)
    
    def _get_category_policies(self, category: str) -> Dict:
        """Obtém políticas específicas da categoria"""
        return POLICIES.get_category_policies(category)


def delegate_task(detection: Dict, context: Optional[Dict] = None) -> Dict:
    """
    Função helper para delegar tarefa
    """
    delegate = TaskDelegate()
    return delegate.delegate(detection, context)


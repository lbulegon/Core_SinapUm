"""
Serviços Agnos para orquestração de alto nível
Coordena múltiplos CrewAI crews e gerencia workflows complexos

NOTA: Este é um template de integração. A estrutura real depende da
implementação específica do framework Agnos.
"""
from typing import Dict, Any, List, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Importar serviços CrewAI
from .crewai_services import (
    analisar_produto_com_crew,
    processar_produto_com_multiplos_agentes,
    CREWAI_AVAILABLE
)

# Tentar importar Agnos
AGNOS_AVAILABLE = False
try:
    # TODO: Ajustar import conforme a estrutura real do Agnos
    # Possíveis importações:
    # from agnos import AgnosOrchestrator, Workflow, State
    # from agnos.core import WorkflowManager
    # import agnos
    
    # Por enquanto, desabilitado até confirmar estrutura
    AGNOS_AVAILABLE = False
    logger.info("Agnos não está disponível ainda. Usando orquestração genérica.")
except ImportError:
    AGNOS_AVAILABLE = False
    logger.warning("Agnos não está instalado. Usando fallback para CrewAI direto.")


class WorkflowManager:
    """
    Gerenciador de workflows genérico.
    Pode ser substituído pela implementação real do Agnos quando disponível.
    """
    
    def __init__(self):
        self.config = getattr(settings, 'AGNOS_CONFIG', {})
        self.state = {}
        self.enabled = self.config.get('enabled', False) and AGNOS_AVAILABLE
    
    def execute_workflow(self, workflow_name: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um workflow específico.
        
        Args:
            workflow_name: Nome do workflow a executar
            inputs: Dados de entrada para o workflow
        
        Returns:
            dict: Resultado do workflow
        """
        if workflow_name == 'analise_completa_produto':
            return self.workflow_analise_completa_produto(
                inputs.get('image_paths', [])
            )
        elif workflow_name == 'validacao_rapida':
            return self.workflow_validacao_rapida(
                inputs.get('produto_data', {})
            )
        else:
            raise ValueError(f"Workflow desconhecido: {workflow_name}")
    
    def workflow_analise_completa_produto(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Workflow completo de análise de produto.
        
        Etapas:
        1. Análise inicial das imagens (CrewAI)
        2. Enriquecimento de dados (CrewAI)
        3. Validação e correção (CrewAI)
        4. Geração de anúncios (CrewAI)
        5. Consolidação final
        """
        logger.info(f"Iniciando workflow de análise completa para {len(image_paths)} imagem(ns)")
        
        if not CREWAI_AVAILABLE:
            return {
                'success': False,
                'error': 'CrewAI não está disponível'
            }
        
        # Etapa 1: Análise das imagens
        resultados_analise = []
        for image_path in image_paths:
            resultado = analisar_produto_com_crew(
                image_path,
                modo_completo=True  # Usa todos os 4 agentes
            )
            resultados_analise.append({
                'image_path': image_path,
                'resultado': resultado
            })
        
        # Etapa 2: Consolidação (se múltiplas imagens)
        if len(resultados_analise) > 1:
            # Consolidar resultados de múltiplas imagens
            produto_consolidado = self._consolidar_resultados(resultados_analise)
        else:
            produto_consolidado = resultados_analise[0]['resultado'] if resultados_analise else None
        
        # Etapa 3: Validação final
        if produto_consolidado and produto_consolidado.get('success'):
            validacao = self._validar_resultado_final(produto_consolidado)
            produto_consolidado['validacao_final'] = validacao
        
        return {
            'success': True,
            'workflow': 'analise_completa_produto',
            'resultado': produto_consolidado,
            'total_imagens': len(image_paths),
            'usando_agnos': AGNOS_AVAILABLE
        }
    
    def workflow_validacao_rapida(self, produto_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Workflow rápido de validação de dados de produto.
        """
        logger.info("Iniciando workflow de validação rápida")
        
        validacao = self._validar_resultado_final(produto_data)
        
        return {
            'success': True,
            'workflow': 'validacao_rapida',
            'produto_data': produto_data,
            'validacao': validacao,
            'usando_agnos': AGNOS_AVAILABLE
        }
    
    def _consolidar_resultados(self, resultados: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolida resultados de múltiplas análises.
        """
        if not resultados:
            return None
        
        # Se todos os resultados são do mesmo produto, consolidar
        primeiro_resultado = resultados[0].get('resultado', {})
        
        # Por enquanto, retorna o primeiro resultado
        # TODO: Implementar lógica de consolidação mais sofisticada
        return primeiro_resultado
    
    def _validar_resultado_final(self, resultado: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida o resultado final da análise.
        """
        validacao = {
            'valido': True,
            'campos_validados': [],
            'campos_faltantes': [],
            'avisos': []
        }
        
        if not resultado or not resultado.get('success'):
            validacao['valido'] = False
            validacao['avisos'].append('Resultado da análise não foi bem-sucedido')
            return validacao
        
        # Validar estrutura básica
        data = resultado.get('result', {})
        if not data:
            validacao['valido'] = False
            validacao['avisos'].append('Dados do produto não encontrados no resultado')
            return validacao
        
        # Validar campos obrigatórios (se houver)
        if 'produto' in data:
            produto = data['produto']
            if not produto.get('nome'):
                validacao['campos_faltantes'].append('produto.nome')
            if not produto.get('marca'):
                validacao['campos_faltantes'].append('produto.marca')
        
        if validacao['campos_faltantes']:
            validacao['valido'] = False
            validacao['avisos'].append(f"Campos obrigatórios faltando: {', '.join(validacao['campos_faltantes'])}")
        
        return validacao


# Instância global do gerenciador
_workflow_manager = None

def get_workflow_manager() -> WorkflowManager:
    """Obtém instância singleton do gerenciador de workflows"""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager


def processar_produto_com_agnos(
    image_paths: List[str],
    workflow_name: str = 'analise_completa_produto'
) -> Dict[str, Any]:
    """
    Função de alto nível para processar produtos usando Agnos (ou fallback).
    
    Args:
        image_paths: Lista de caminhos das imagens
        workflow_name: Nome do workflow a executar
    
    Returns:
        dict: Resultado do processamento
    """
    manager = get_workflow_manager()
    
    inputs = {
        'image_paths': image_paths
    }
    
    return manager.execute_workflow(workflow_name, inputs)


def validar_produto_com_agnos(produto_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida dados de produto usando workflow do Agnos.
    
    Args:
        produto_data: Dados do produto a validar
    
    Returns:
        dict: Resultado da validação
    """
    manager = get_workflow_manager()
    
    inputs = {
        'produto_data': produto_data
    }
    
    return manager.execute_workflow('validacao_rapida', inputs)


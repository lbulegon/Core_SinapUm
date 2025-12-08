# Integração Agnos + OpenMind + CrewAI + Django (VitrineZap)

## 📋 Visão Geral

Este documento descreve como integrar o **Agnos** junto com **CrewAI** e **OpenMind** no projeto **VitrineZap Django**.

## 🎯 Objetivos da Integração Agnos

O Agnos será integrado para:
- **Orquestração de alto nível**: Coordenar múltiplos crews do CrewAI
- **Gerenciamento de estado**: Manter estado entre diferentes processos
- **Workflow complexo**: Gerenciar fluxos de trabalho mais complexos que envolvem múltiplos crews
- **Interface unificada**: Abstrair a complexidade de múltiplos sistemas de agentes

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────┐
│                    Django (VitrineZap)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Views / API Endpoints                       │  │
│  └─────────────────┬────────────────────────────────────┘  │
│                    │                                        │
│  ┌─────────────────▼────────────────────────────────────┐  │
│  │        Agnos Orchestrator (Alto Nível)               │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │   Gerenciamento de Workflows e Estado        │   │  │
│  │  └────────────────┬─────────────────────────────┘   │  │
│  └───────────────────┼──────────────────────────────────┘  │
│                      │                                      │
│  ┌───────────────────▼──────────────────────────────────┐  │
│  │        CrewAI Crews (Médio Nível)                    │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │  │
│  │  │ Crew       │  │ Crew       │  │ Crew       │    │  │
│  │  │ Análise    │  │ Validação  │  │ Geração    │    │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘    │  │
│  └────────┼───────────────┼───────────────┼────────────┘  │
│           │               │               │                │
│           └───────────────┴───────────────┘                │
│                           │                                │
│           ┌───────────────▼───────────────┐                │
│           │    OpenMind AI Server         │                │
│           │  (Análise de Imagens + LLM)   │                │
│           └───────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Hierarquia de Integração

1. **Agnos (Nível 1 - Orquestrador Principal)**
   - Gerencia workflows complexos
   - Coordena múltiplos crews do CrewAI
   - Mantém estado global do processo

2. **CrewAI (Nível 2 - Equipes de Agentes)**
   - Equipes especializadas de agentes
   - Cada crew tem responsabilidades específicas
   - Executam tarefas coordenadas

3. **OpenMind (Nível 3 - Backend de IA)**
   - Análise de imagens
   - LLM backend para os agentes
   - Processamento multimodal

## 📦 Instalação

### 1. Verificar se Agnos já está instalado

```bash
pip list | grep -i agnos
```a\Q1\

### 2. Instalar Agnos (se necessário)

```bash
# Opção 1: Via pip (se disponível no PyPI\)
pip install agnos

# Opção 2: Via git (se for repositório)
pip install git+https://github.com/seu-usuario/agnos.git

# Opção 3: Instalação local (se você tem o código)
cd /caminho/para/agnos
pip install -e .
```

## 🔧 Configuração

### 1. Configurar no settings.py

```python
# settings.py

# OpenMind AI (já existe)
OPENMIND_AI_URL = 'http://127.0.0.1:5000'
OPENMIND_AI_KEY = 'sua_chave_openmind'

# CrewAI Configuration
CREWAI_CONFIG = {
    'default_llm': 'openmind',
    'temperature': 0.7,
    'max_iterations': 3,
}

# Agnos Configuration
AGNOS_CONFIG = {
    'enabled': True,
    'default_workflow': 'produto_completo',
    'state_persistence': True,
    'state_backend': 'memory',  # ou 'redis', 'database'
    'max_concurrent_crews': 3,
    'timeout': 300,  # segundos
}

# OpenMind.org Configuration (para LLMs)
OPENMIND_ORG_BASE_URL = 'https://api.openmind.org/api/core/openai'
OPENMIND_ORG_API_KEY = OPENMIND_AI_KEY
OPENMIND_ORG_MODEL = 'gpt-4o'
```

## 📝 Implementação

### Estrutura de Arquivos

```
app_sinapum/
├── crewai_services.py       # CrewAI (já criado)
├── agnos_services.py        # Agnos (a criar)
├── services.py              # OpenMind direto (já existe)
└── views_agnos.py           # Views para Agnos (a criar)
```

### Exemplo de Integração Agnos

Criar `/root/SinapUm/app_sinapum/agnos_services.py`:

```python
"""
Serviços Agnos para orquestração de alto nível
Coordena múltiplos CrewAI crews e gerencia workflows complexos
"""
from typing import Dict, Any, List, Optional
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# Tentar importar Agnos
try:
    # TODO: Ajustar import conforme a estrutura real do Agnos
    # from agnos import AgnosOrchestrator, Workflow, State
    AGNOS_AVAILABLE = False  # Temporariamente False até confirmar estrutura
    logger.warning("Agnos não está disponível. Estrutura de importação a definir.")
except ImportError:
    AGNOS_AVAILABLE = False
    logger.warning("Agnos não está instalado ou não encontrado.")


class AgnosWorkflowManager:
    """
    Gerencia workflows usando Agnos.
    Coordena múltiplos CrewAI crews para processos complexos.
    """
    
    def __init__(self):
        self.config = getattr(settings, 'AGNOS_CONFIG', {})
        self.state = {}
    
    def workflow_analise_completa_produto(self, image_paths: List[str]) -> Dict[str, Any]:
        """
        Workflow completo de análise de produto usando Agnos + CrewAI.
        
        Etapas:
        1. Análise inicial das imagens (CrewAI Crew de Análise)
        2. Enriquecimento de dados (CrewAI Crew de Enriquecimento)
        3. Validação e correção (CrewAI Crew de Validação)
        4. Geração de anúncios (CrewAI Crew de Geração)
        5. Consolidação final (Agnos)
        """
        if not AGNOS_AVAILABLE:
            # Fallback para CrewAI direto
            from .crewai_services import analisar_produto_com_crew
            return analisar_produto_com_crew(image_paths[0] if image_paths else None)
        
        # TODO: Implementar workflow real com Agnos
        # workflow = AgnosWorkflow("analise_completa")
        # workflow.add_step("analise", self._crew_analise)
        # workflow.add_step("enriquecimento", self._crew_enriquecimento)
        # workflow.add_step("validacao", self._crew_validacao)
        # workflow.add_step("geracao", self._crew_geracao)
        # return workflow.execute(image_paths)
        
        pass
    
    def workflow_validacao_rapida(self, produto_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Workflow rápido de validação usando apenas CrewAI de Validação.
        """
        # TODO: Implementar com Agnos
        pass


def processar_produto_com_agnos(image_paths: List[str]) -> Dict[str, Any]:
    """
    Função de alto nível para processar produtos usando Agnos.
    """
    manager = AgnosWorkflowManager()
    return manager.workflow_analise_completa_produto(image_paths)
```

## 🔍 Próximos Passos

Para completar a integração do Agnos, precisamos:

1. **Confirmar estrutura do Agnos**:
   - [ ] Qual é a estrutura de imports do Agnos?
   - [ ] Como criar workflows no Agnos?
   - [ ] Como o Agnos gerencia estado?
   - [ ] Qual é a API do Agnos?

2. **Implementar integração**:
   - [ ] Criar `agnos_services.py` com a estrutura real
   - [ ] Integrar Agnos com CrewAI
   - [ ] Criar workflows específicos do VitrineZap
   - [ ] Implementar persistência de estado

3. **Criar views Django**:
   - [ ] Criar `views_agnos.py`
   - [ ] Adicionar rotas no `urls.py`
   - [ ] Criar templates (opcional)

## ❓ Informações Necessárias

Para completar a integração, precisamos saber:

1. **O que é o Agnos?**
   - É um framework Python?
   - É um serviço externo?
   - É código próprio/interno?

2. **Como instalar?**
   - Está no PyPI?
   - É um repositório Git?
   - Precisa ser compilado/instalado de outra forma?

3. **Como usar?**
   - Exemplo de código
   - Documentação disponível
   - Estrutura de API

4. **Qual o objetivo da integração?**
   - Orquestração de múltiplos crews?
   - Gerenciamento de estado?
   - Workflow específico?

## 📚 Referências

- Agnos: [Link para documentação/README]
- CrewAI: https://docs.crewai.com/
- OpenMind: https://docs.openmind.org/

## 🔄 Alternativa: Implementação Genérica

Se o Agnos ainda não estiver disponível ou não tivermos os detalhes, podemos criar uma **camada de orquestração genérica** que:

1. Coordena múltiplos CrewAI crews
2. Gerencia estado entre processos
3. Implementa workflows complexos
4. Pode ser substituída pelo Agnos real quando disponível

Isso permite começar a usar a arquitetura enquanto obtemos mais informações sobre o Agnos específico.


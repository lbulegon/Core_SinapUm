# 🧠 Estratégia de Transformação: SinapUm → Master Control Program (MCP)

## 📋 Visão Geral

Este documento descreve a estratégia para transformar o **SinapUm** (atualmente um servidor Django) em um **Master Control Program (MCP)** - um orquestrador central que coordena múltiplos agentes, LLMs e serviços do ecossistema Évora.

**Objetivo:** Criar um cérebro central que recebe tarefas, decide qual agente/serviço deve processar, orquestra a execução e retorna respostas padronizadas - **sem quebrar nada do que já existe**.

---

## 🎯 Princípios da Transformação

### 1. **Zero Breaking Changes**
- ✅ Todos os endpoints existentes continuam funcionando
- ✅ Views Django atuais permanecem intactas
- ✅ Integrações existentes (OpenMind, CrewAI, Agnos) não são alteradas
- ✅ MCP é uma **camada adicional**, não uma substituição

### 2. **Evolução Gradual**
- Fase 1: Estrutura MCP + Endpoint principal
- Fase 2: Migração gradual de endpoints para agentes
- Fase 3: Adição de novos módulos (MotoPro, SparkScore, KMN)

### 3. **Modularidade**
- Cada funcionalidade vira um **agente** independente
- Agentes podem ser plugados/desplugados sem afetar outros
- Comunicação padronizada via schemas

---

## 🏗️ Arquitetura Proposta

### Estrutura de Diretórios

```
SinapUm/
├── app_sinapum/                    # App Django existente (mantido)
│   ├── views.py                    # Views atuais (mantidas)
│   ├── services.py                  # Serviços atuais (mantidos)
│   ├── models.py                   # Models atuais (mantidos)
│   └── ...
│
├── mcp/                            # 🆕 Módulo MCP (novo)
│   ├── __init__.py
│   ├── core/                       # Núcleo do MCP
│   │   ├── __init__.py
│   │   ├── router.py               # Roteador principal (/mcp/route-task)
│   │   ├── registry.py             # Registro de agentes disponíveis
│   │   └── telemetry.py            # Logs e métricas
│   │
│   ├── agents/                     # Agentes do MCP
│   │   ├── __init__.py
│   │   ├── agent_vitrinezap.py     # Agente de produtos/catálogo
│   │   ├── agent_openmind.py       # Agente de análise de imagens
│   │   ├── agent_crewai.py         # Agente CrewAI (orquestração)
│   │   ├── agent_agnos.py          # Agente Agnos (workflows)
│   │   └── agent_motopro.py        # 🚧 Futuro: Agente MotoPro
│   │
│   ├── schemas/                    # Schemas Pydantic
│   │   ├── __init__.py
│   │   ├── task_schema.py          # TaskRequest, TaskResponse
│   │   ├── produto_schema.py       # Schema oficial do produto
│   │   └── common_schema.py        # Schemas compartilhados
│   │
│   └── utils/                      # Utilitários MCP
│       ├── __init__.py
│       ├── validators.py           # Validações
│       └── formatters.py           # Formatação de respostas
│
└── setup/                          # Configuração Django (mantida)
    ├── urls.py                     # Adicionar rotas MCP
    └── settings.py                 # Configurações (mantidas)
```

---

## 🔄 Fluxo MCP

### Antes (Atual)

```
Cliente → Django View → Service → OpenMind/CrewAI/Agnos → Resposta
```

### Depois (MCP)

```
Cliente → MCP Router → Agente → Service → OpenMind/CrewAI/Agnos → MCP Response
         ↓
    (Telemetria)
         ↓
    (Logs estruturados)
```

### Compatibilidade

```
Cliente → Django View → Service → OpenMind → Resposta  ✅ (continua funcionando)
Cliente → MCP Router → Agent → Service → OpenMind → Resposta  🆕 (novo caminho)
```

---

## 📡 Endpoint Principal MCP

### `/mcp/route-task` (POST)

**Request:**
```json
{
  "contexto": "vitrinezap",
  "tipo_tarefa": "analisar_imagem_produto",
  "dados": {
    "image": "base64_ou_url",
    "language": "pt-BR"
  },
  "metadata": {
    "requisitante": "vitrinezap",
    "prioridade": "normal",
    "timeout": 60
  }
}
```

**Response:**
```json
{
  "sucesso": true,
  "resultado": {
    "produto": { ... },
    "image_url": "http://...",
    "image_path": "media/uploads/..."
  },
  "agente_usado": "agent_openmind",
  "tempo_processamento_ms": 1234,
  "metadata": {
    "processado_por": "SinapUm MCP",
    "timestamp": "2025-12-11T14:30:00Z",
    "versao_mcp": "1.0.0"
  }
}
```

---

## 🔌 Agentes do MCP

### 1. Agent VitrineZap (`agent_vitrinezap.py`)

**Responsabilidades:**
- Preparar cadastro de produtos
- Validar dados de produtos
- Transformar formatos (ÉVORA → modelo.json)
- Gerenciar catálogo

**Tarefas suportadas:**
- `preparar_cadastro_produto`
- `validar_produto`
- `transformar_formato`

**Integração:**
- Usa `app_sinapum.services` existente
- Usa `app_sinapum.utils.transform_evora_to_modelo_json`

### 2. Agent OpenMind (`agent_openmind.py`)

**Responsabilidades:**
- Análise de imagens de produtos
- Extração de dados via IA
- Geração de JSON estruturado

**Tarefas suportadas:**
- `analisar_imagem_produto`
- `enriquecer_dados_produto`

**Integração:**
- Chama OpenMind AI Server (porta 8000)
- Usa `app_sinapum.services.analyze_image_with_openmind`

### 3. Agent CrewAI (`agent_crewai.py`)

**Responsabilidades:**
- Orquestração de múltiplos agentes
- Análise complexa com múltiplas LLMs
- Workflows de análise avançada

**Tarefas suportadas:**
- `analisar_com_crewai`
- `orquestrar_analise_completa`

**Integração:**
- Usa `app_sinapum.crewai_services`
- Mantém compatibilidade com views CrewAI existentes

### 4. Agent Agnos (`agent_agnos.py`)

**Responsabilidades:**
- Workflows de alto nível
- Validação de dados
- Processamento em pipeline

**Tarefas suportadas:**
- `executar_workflow_agnos`
- `validar_com_agnos`

**Integração:**
- Usa `app_sinapum.agnos_services`
- Mantém compatibilidade com views Agnos existentes

---

## 📝 Schemas (Pydantic)

### TaskRequest

```python
from pydantic import BaseModel
from typing import Any, Dict, Optional
from datetime import datetime

class TaskRequest(BaseModel):
    contexto: str  # "vitrinezap", "motopro", "sparkscore", etc.
    tipo_tarefa: str  # "analisar_imagem", "preparar_cadastro", etc.
    dados: Dict[str, Any]  # Dados específicos da tarefa
    metadata: Optional[Dict[str, Any]] = None
```

### TaskResponse

```python
class TaskResponse(BaseModel):
    sucesso: bool
    resultado: Optional[Dict[str, Any]] = None
    erro: Optional[str] = None
    codigo_erro: Optional[str] = None
    agente_usado: Optional[str] = None
    tempo_processamento_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
```

### ProdutoSchema (Oficial)

```python
class ProdutoSchema(BaseModel):
    """Schema oficial do produto no formato modelo.json"""
    produto: Dict[str, Any]
    produto_generico_catalogo: Dict[str, Any]
    produto_viagem: Dict[str, Any]
    estabelecimento: Dict[str, Any]
    campanha: Dict[str, Any]
    shopper: Dict[str, Any]
    cadastro_meta: Dict[str, Any]
```

---

## 🚀 Plano de Implementação

### Fase 1: Fundação (Semana 1)

**Objetivo:** Criar estrutura MCP sem alterar nada existente

**Tarefas:**
1. ✅ Criar diretório `mcp/` e subdiretórios
2. ✅ Criar schemas básicos (`task_schema.py`)
3. ✅ Criar router MCP (`mcp/core/router.py`)
4. ✅ Criar registry de agentes (`mcp/core/registry.py`)
5. ✅ Adicionar rota `/mcp/route-task` no Django
6. ✅ Criar primeiro agente (Agent OpenMind) como prova de conceito

**Critério de Sucesso:**
- Endpoint `/mcp/route-task` responde
- Agent OpenMind funciona via MCP
- Endpoints Django antigos continuam funcionando

### Fase 2: Migração Gradual (Semana 2-3)

**Objetivo:** Migrar funcionalidades existentes para agentes

**Tarefas:**
1. ✅ Criar Agent VitrineZap
2. ✅ Criar Agent CrewAI
3. ✅ Criar Agent Agnos
4. ✅ Adicionar telemetria básica
5. ✅ Documentar todos os agentes

**Critério de Sucesso:**
- Todos os agentes funcionam via MCP
- Telemetria registra execuções
- Documentação completa

### Fase 3: Expansão (Futuro)

**Objetivo:** Adicionar novos módulos ao MCP

**Tarefas:**
1. 🚧 Agent MotoPro (distribuição de vagas, turnos, raio 300m)
2. 🚧 Agent SparkScore (análise psicológica, PPA, pontuação)
3. 🚧 Agent KMN (Keeper Mesh Network, decisões de entrega)
4. 🚧 Agent Pagamentos (split, margem dinâmica, comissões)

---

## 🔧 Implementação Técnica

### 1. Router MCP (`mcp/core/router.py`)

```python
from typing import Dict, Any
from mcp.schemas.task_schema import TaskRequest, TaskResponse
from mcp.core.registry import AgentRegistry
from mcp.core.telemetry import log_task_execution

class MCPRouter:
    def __init__(self):
        self.registry = AgentRegistry()
    
    def route_task(self, task: TaskRequest) -> TaskResponse:
        """Roteia tarefa para o agente apropriado"""
        start_time = time.time()
        
        # Encontrar agente
        agent = self.registry.get_agent(task.contexto, task.tipo_tarefa)
        
        if not agent:
            return TaskResponse(
                sucesso=False,
                erro=f"Agente não encontrado para contexto '{task.contexto}' e tarefa '{task.tipo_tarefa}'",
                codigo_erro="AGENT_NOT_FOUND"
            )
        
        # Executar agente
        try:
            resultado = agent.execute(task.dados)
            tempo_ms = int((time.time() - start_time) * 1000)
            
            # Log
            log_task_execution(task, resultado, tempo_ms, agent.name)
            
            return TaskResponse(
                sucesso=True,
                resultado=resultado,
                agente_usado=agent.name,
                tempo_processamento_ms=tempo_ms,
                metadata={
                    "processado_por": "SinapUm MCP",
                    "timestamp": datetime.now().isoformat(),
                    "versao_mcp": "1.0.0"
                }
            )
        except Exception as e:
            tempo_ms = int((time.time() - start_time) * 1000)
            log_task_execution(task, None, tempo_ms, agent.name, error=str(e))
            
            return TaskResponse(
                sucesso=False,
                erro=str(e),
                codigo_erro="EXECUTION_ERROR",
                agente_usado=agent.name,
                tempo_processamento_ms=tempo_ms
            )
```

### 2. Registry de Agentes (`mcp/core/registry.py`)

```python
from typing import Dict, Optional
from mcp.agents.base_agent import BaseAgent

class AgentRegistry:
    def __init__(self):
        self.agents: Dict[tuple, BaseAgent] = {}
    
    def register(self, contexto: str, tipo_tarefa: str, agent: BaseAgent):
        """Registra um agente"""
        key = (contexto, tipo_tarefa)
        self.agents[key] = agent
    
    def get_agent(self, contexto: str, tipo_tarefa: str) -> Optional[BaseAgent]:
        """Retorna agente para contexto e tarefa"""
        key = (contexto, tipo_tarefa)
        return self.agents.get(key)
    
    def list_agents(self) -> Dict[str, list]:
        """Lista todos os agentes registrados"""
        result = {}
        for (contexto, tarefa), agent in self.agents.items():
            if contexto not in result:
                result[contexto] = []
            result[contexto].append({
                "tarefa": tarefa,
                "agente": agent.name,
                "descricao": agent.description
            })
        return result
```

### 3. Base Agent (`mcp/agents/base_agent.py`)

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Executa a tarefa do agente"""
        pass
    
    def validate(self, dados: Dict[str, Any]) -> bool:
        """Valida dados de entrada"""
        return True
```

### 4. Agent OpenMind (Exemplo) (`mcp/agents/agent_openmind.py`)

```python
from mcp.agents.base_agent import BaseAgent
from app_sinapum.services import analyze_image_with_openmind
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class AgentOpenMind(BaseAgent):
    def __init__(self):
        super().__init__(
            name="agent_openmind",
            description="Agente de análise de imagens usando OpenMind AI"
        )
    
    def execute(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa imagem de produto"""
        # Validar entrada
        if 'image' not in dados:
            raise ValueError("Campo 'image' é obrigatório")
        
        # Chamar serviço existente (sem alterar)
        image_file = dados['image']
        image_path = dados.get('image_path')
        image_url = dados.get('image_url')
        language = dados.get('language', 'pt-BR')
        
        # Usar serviço Django existente
        result = analyze_image_with_openmind(
            image_file,
            image_path=image_path,
            image_url=image_url
        )
        
        return result
```

### 5. View Django para MCP (`app_sinapum/views_mcp.py`)

```python
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from mcp.core.router import MCPRouter
from mcp.schemas.task_schema import TaskRequest, TaskResponse
import json
import logging

logger = logging.getLogger(__name__)

router = MCPRouter()

@csrf_exempt
@require_http_methods(["POST"])
def mcp_route_task(request):
    """
    Endpoint principal do MCP
    POST /mcp/route-task
    """
    try:
        # Parse JSON
        data = json.loads(request.body)
        
        # Validar e criar TaskRequest
        task = TaskRequest(**data)
        
        # Rotear tarefa
        response = router.route_task(task)
        
        # Retornar resposta
        return JsonResponse(response.dict(), status=200 if response.sucesso else 500)
    
    except json.JSONDecodeError:
        return JsonResponse({
            "sucesso": False,
            "erro": "JSON inválido",
            "codigo_erro": "INVALID_JSON"
        }, status=400)
    
    except Exception as e:
        logger.error(f"Erro no MCP router: {str(e)}", exc_info=True)
        return JsonResponse({
            "sucesso": False,
            "erro": str(e),
            "codigo_erro": "INTERNAL_ERROR"
        }, status=500)

@require_http_methods(["GET"])
def mcp_list_agents(request):
    """
    Lista agentes disponíveis
    GET /mcp/agents
    """
    agents = router.registry.list_agents()
    return JsonResponse({
        "sucesso": True,
        "agentes": agents
    })
```

### 6. Adicionar Rotas no Django (`setup/urls.py`)

```python
# Adicionar após as rotas existentes
from app_sinapum import views_mcp

urlpatterns += [
    # MCP endpoints
    path('mcp/route-task', views_mcp.mcp_route_task, name='mcp_route_task'),
    path('mcp/agents', views_mcp.mcp_list_agents, name='mcp_list_agents'),
]
```

---

## 📊 Telemetria e Logs

### Estrutura de Logs

```python
# mcp/core/telemetry.py
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger('mcp.telemetry')

def log_task_execution(
    task: TaskRequest,
    resultado: Optional[Dict],
    tempo_ms: int,
    agente: str,
    error: Optional[str] = None
):
    """Registra execução de tarefa"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "contexto": task.contexto,
        "tipo_tarefa": task.tipo_tarefa,
        "agente": agente,
        "tempo_ms": tempo_ms,
        "sucesso": resultado is not None,
        "erro": error
    }
    
    if error:
        logger.error(f"MCP Task Failed: {log_data}")
    else:
        logger.info(f"MCP Task Executed: {log_data}")
```

### Métricas Coletadas

- Tempo de processamento por agente
- Taxa de sucesso/erro
- Agentes mais utilizados
- Contextos mais frequentes
- Tipos de tarefa mais comuns

---

## 🔄 Compatibilidade e Migração

### Estratégia de Compatibilidade

1. **Endpoints Django antigos continuam funcionando**
   - `/api/v1/analyze-product-image` → Funciona normalmente
   - `/analyze/` → Funciona normalmente
   - Todas as views existentes → Funcionam normalmente

2. **MCP é uma camada adicional**
   - Clientes podem usar endpoints antigos OU MCP
   - Migração gradual conforme necessário

3. **Agentes usam serviços existentes**
   - Agent OpenMind → `app_sinapum.services.analyze_image_with_openmind`
   - Agent VitrineZap → `app_sinapum.utils.transform_evora_to_modelo_json`
   - Nenhum código existente é alterado

### Exemplo de Migração Gradual

**Antes:**
```python
# Cliente chama diretamente
POST /api/v1/analyze-product-image
```

**Depois (opcional):**
```python
# Cliente pode usar MCP
POST /mcp/route-task
{
  "contexto": "vitrinezap",
  "tipo_tarefa": "analisar_imagem_produto",
  "dados": { ... }
}
```

**Ambos funcionam simultaneamente!**

---

## 📦 Dependências

### Novas Dependências

```txt
# Adicionar ao requirements.txt
pydantic>=2.0.0  # Para schemas
```

### Dependências Existentes (mantidas)

- Django (já existe)
- requests (já existe)
- Todas as outras (mantidas)

---

## 🧪 Testes

### Teste 1: Endpoint MCP

```bash
curl -X POST http://69.169.102.84:5000/mcp/route-task \
  -H "Content-Type: application/json" \
  -d '{
    "contexto": "vitrinezap",
    "tipo_tarefa": "analisar_imagem_produto",
    "dados": {
      "image_url": "http://...",
      "language": "pt-BR"
    }
  }'
```

### Teste 2: Listar Agentes

```bash
curl http://69.169.102.84:5000/mcp/agents
```

### Teste 3: Compatibilidade

```bash
# Endpoint antigo deve continuar funcionando
curl -X POST http://69.169.102.84:5000/api/v1/analyze-product-image \
  -F "image=@test.jpg"
```

---

## 📈 Roadmap Futuro

### Módulos Futuros

1. **Agent MotoPro**
   - Distribuição inteligente de vagas
   - Lógica de turnos e raio 300m
   - IA de priorização
   - Compliance de rotas

2. **Agent SparkScore**
   - Análise psicológica e semiótica
   - PPA automático
   - Pontuação de ofertas
   - Priorização de campanhas

3. **Agent KMN (Keeper Mesh Network)**
   - Decisão de qual Keeper entrega
   - Resolução de conflitos de carteira
   - Otimização de rota social

4. **Agent Pagamentos**
   - Split Shopper/Keeper
   - Margem dinâmica
   - Regras de comissão Mesh

---

## ✅ Checklist de Implementação

### Fase 1: Fundação
- [ ] Criar estrutura de diretórios `mcp/`
- [ ] Criar schemas (`task_schema.py`, `produto_schema.py`)
- [ ] Criar router MCP (`mcp/core/router.py`)
- [ ] Criar registry (`mcp/core/registry.py`)
- [ ] Criar base agent (`mcp/agents/base_agent.py`)
- [ ] Criar Agent OpenMind (prova de conceito)
- [ ] Adicionar view Django (`views_mcp.py`)
- [ ] Adicionar rotas no `urls.py`
- [ ] Testar endpoint `/mcp/route-task`
- [ ] Verificar compatibilidade com endpoints antigos

### Fase 2: Migração
- [ ] Criar Agent VitrineZap
- [ ] Criar Agent CrewAI
- [ ] Criar Agent Agnos
- [ ] Adicionar telemetria
- [ ] Documentar todos os agentes
- [ ] Criar testes automatizados

### Fase 3: Expansão
- [ ] Agent MotoPro
- [ ] Agent SparkScore
- [ ] Agent KMN
- [ ] Agent Pagamentos

---

## 🎯 Benefícios da Transformação

### 1. **Ordem e Organização**
- Cada tarefa tem contexto claro
- Nada fica misturado
- Fácil de entender e manter

### 2. **Escalabilidade**
- Novos módulos podem ser plugados facilmente
- Sem bagunçar código existente
- Crescimento sustentável

### 3. **Telemetria Automática**
- Logs estruturados de todas as execuções
- Métricas de performance
- Base para futuras IAs coordenadoras

### 4. **Ponto Único de Coordenação**
- Quando adicionar inteligência de rota, priorização, PPA
- Tudo já estará preparado
- MCP coordena tudo

### 5. **Rastreabilidade**
- Cada decisão vira dado útil
- Histórico completo de execuções
- Base para aprendizado futuro

---

## 🔒 Garantias de Não-Quebra

### ✅ O que NÃO muda:

1. **Endpoints Django existentes**
   - `/api/v1/analyze-product-image` → Continua funcionando
   - `/analyze/` → Continua funcionando
   - Todas as views → Continuam funcionando

2. **Serviços existentes**
   - `app_sinapum.services` → Não alterado
   - `app_sinapum.utils` → Não alterado
   - Integrações OpenMind/CrewAI/Agnos → Não alteradas

3. **Models e banco de dados**
   - `app_sinapum.models` → Não alterado
   - Banco de dados PostgreSQL → Configurado

4. **Configurações**
   - `setup/settings.py` → Apenas adições (não remoções)
   - Variáveis de ambiente → Mantidas

### 🆕 O que é adicionado:

1. **Nova estrutura `mcp/`**
   - Não interfere com código existente
   - Pode ser ignorada se necessário

2. **Novos endpoints**
   - `/mcp/route-task` → Novo
   - `/mcp/agents` → Novo
   - Não substituem endpoints antigos

3. **Novos schemas**
   - Apenas para MCP
   - Não afetam código existente

---

## 📚 Documentação

### Documentos a Criar

1. **README_MCP.md** - Visão geral do MCP
2. **AGENTES.md** - Documentação de cada agente
3. **API_MCP.md** - Documentação da API MCP
4. **MIGRACAO.md** - Guia de migração gradual

---

## 🎬 Próximos Passos Imediatos

1. **Criar estrutura de diretórios**
   ```bash
   mkdir -p app_sinapum/mcp/{core,agents,schemas,utils}
   ```

2. **Instalar dependências**
   ```bash
   pip install pydantic>=2.0.0
   ```

3. **Criar arquivos base**
   - `mcp/schemas/task_schema.py`
   - `mcp/core/router.py`
   - `mcp/core/registry.py`
   - `mcp/agents/base_agent.py`

4. **Implementar primeiro agente**
   - `mcp/agents/agent_openmind.py`

5. **Adicionar view e rota**
   - `app_sinapum/views_mcp.py`
   - Adicionar em `setup/urls.py`

6. **Testar**
   - Endpoint `/mcp/route-task`
   - Verificar compatibilidade

---

## 🏁 Conclusão

Esta estratégia transforma o SinapUm em um **verdadeiro Master Control Program** mantendo **100% de compatibilidade** com o código existente.

O MCP será:
- ✅ **Orquestrador central** de todos os agentes
- ✅ **Ponto único** de entrada para tarefas complexas
- ✅ **Base** para futuras expansões (MotoPro, SparkScore, KMN)
- ✅ **Rastreável** e **telemetrado**
- ✅ **Modular** e **escalável**

**Sem quebrar nada do que já funciona!**

---

**Data de Criação:** 2025-01-10  
**Versão:** 1.0.0  
**Status:** Estratégia aprovada - Pronto para implementação


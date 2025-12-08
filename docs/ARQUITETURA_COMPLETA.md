# 🏗️ Arquitetura Completa: Agnos + CrewAI + OpenMind + Django

## 📊 Visão Geral da Integração

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Django (VitrineZap)                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                  Views / API Endpoints                        │  │
│  │  - /analyze/              (OpenMind direto)                  │  │
│  │  - /analyze/crewai/       (CrewAI)                           │  │
│  │  - /analyze/agnos/        (Agnos - orquestração completa)    │  │
│  └─────────────────┬────────────────────────────────────────────┘  │
│                    │                                                │
│  ┌─────────────────▼────────────────────────────────────────────┐  │
│  │           Agnos (Nível 1 - Orquestrador Principal)          │  │
│  │  • Gerencia workflows complexos                              │  │
│  │  • Coordena múltiplos CrewAI crews                           │  │
│  │  • Mantém estado global                                      │  │
│  └─────────────────┬────────────────────────────────────────────┘  │
│                    │                                                │
│  ┌─────────────────▼────────────────────────────────────────────┐  │
│  │        CrewAI (Nível 2 - Equipes de Agentes)                │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │  │
│  │  │ Crew Análise │  │ Crew         │  │ Crew         │      │  │
│  │  │              │  │ Enriquecimento│  │ Geração      │      │  │
│  │  │ • Agente     │  │ • Agente     │  │ • Agente     │      │  │
│  │  │   Análise    │  │   Enriquec.  │  │   Validação  │      │  │
│  │  │              │  │              │  │ • Agente     │      │  │
│  │  │              │  │              │  │   Geração    │      │  │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │  │
│  └─────────┼──────────────────┼──────────────────┼──────────────┘  │
│            │                  │                  │                  │
│            └──────────────────┴──────────────────┘                  │
│                            │                                        │
│            ┌───────────────▼───────────────┐                        │
│            │    OpenMind (Nível 3)         │                        │
│            │  ┌─────────────────────────┐  │                        │
│            │  │ OpenMind AI Server      │  │                        │
│            │  │ • Análise de Imagens    │  │                        │
│            │  │ • Vision API            │  │                        │
│            │  └──────────┬──────────────┘  │                        │
│            │             │                 │                        │
│            │  ┌──────────▼──────────────┐  │                        │
│            │  │ OpenMind.org            │  │                        │
│            │  │ • LLM Backend           │  │                        │
│            │  │ • Múltiplos modelos     │  │                        │
│            │  │   (OpenAI, Anthropic,   │  │                        │
│            │  │    Gemini, etc.)        │  │                        │
│            │  └─────────────────────────┘  │                        │
│            └───────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎯 Níveis de Integração

### Nível 1: Agnos (Orquestrador Principal)
- **Responsabilidade**: Coordenação de alto nível, gerenciamento de workflows
- **Uso**: Para processos complexos que envolvem múltiplos crews
- **Arquivo**: `app_sinapum/agnos_services.py`

### Nível 2: CrewAI (Equipes de Agentes)
- **Responsabilidade**: Orquestração de agentes especializados
- **Uso**: Para tarefas que precisam de múltiplos agentes trabalhando juntos
- **Arquivo**: `app_sinapum/crewai_services.py`

### Nível 3: OpenMind (Backend de IA)
- **Responsabilidade**: 
  - Análise de imagens (OpenMind AI Server)
  - LLM backend para agentes (OpenMind.org)
- **Uso**: Processamento de imagens e geração de texto
- **Arquivos**: 
  - `app_sinapum/services.py` (integração direta)
  - OpenMind AI Server em `/opt/openmind-ai/`

## 🔄 Fluxos de Trabalho

### Fluxo 1: Análise Direta (OpenMind)
```
Upload Imagem → OpenMind AI Server → Dados Extraídos → PostgreSQL
```
**Quando usar**: Análise simples e rápida

### Fluxo 2: Análise com CrewAI
```
Upload Imagem → CrewAI Crew → 
  ├─ Agente Análise → OpenMind
  ├─ Agente Enriquecimento → APIs
  ├─ Agente Validação
  └─ Agente Geração
→ Dados Consolidados → PostgreSQL
```
**Quando usar**: Análise completa com múltiplos agentes

### Fluxo 3: Análise com Agnos (Completo)
```
Upload Múltiplas Imagens → Agnos Workflow →
  ├─ Crew Análise Completa (CrewAI)
  │   ├─ Análise de cada imagem
  │   └─ Consolidação
  ├─ Crew Validação (CrewAI)
  │   └─ Validação cruzada
  └─ Crew Geração (CrewAI)
      └─ Anúncios prontos
→ Resultado Final Consolidado → PostgreSQL
```
**Quando usar**: Processos complexos com múltiplas imagens e validações

## 📁 Estrutura de Arquivos

```
app_sinapum/
├── services.py              # OpenMind direto (já existe)
├── crewai_services.py       # CrewAI (criado)
├── agnos_services.py        # Agnos (criado)
├── views.py                 # Views principais (já existe)
├── views_crewai.py          # Views CrewAI (criado)
├── views_agnos.py           # Views Agnos (criado)
└── models.py                # Modelos Django (já existe)

setup/
├── settings.py              # Configurações (atualizado)
└── urls.py                  # Rotas (atualizado)

docs/
├── INTEGRACAO_CREWAI_OPENMIND.md
├── INTEGRACAO_AGNOS.md
├── ARQUITETURA_COMPLETA.md  (este arquivo)
└── COMO_USAR_OPENMIND_COMO_LLM.md
```

## 🔧 Configuração

### settings.py

```python
# OpenMind AI (Nível 3)
OPENMIND_AI_URL = 'http://127.0.0.1:5000'
OPENMIND_AI_KEY = 'sua_chave_openmind'

# OpenMind.org (LLM Backend)
OPENMIND_ORG_BASE_URL = 'https://api.openmind.org/api/core/openai'
OPENMIND_ORG_API_KEY = OPENMIND_AI_KEY  # Mesma chave!
OPENMIND_ORG_MODEL = 'gpt-4o'

# CrewAI (Nível 2)
CREWAI_CONFIG = {
    'default_llm': 'openmind',  # Usa OpenMind.org
    'temperature': 0.7,
    'max_iterations': 3,
}

# Agnos (Nível 1)
AGNOS_CONFIG = {
    'enabled': True,
    'default_workflow': 'analise_completa_produto',
    'state_persistence': True,
    'state_backend': 'memory',
    'max_concurrent_crews': 3,
    'timeout': 300,
}
```

## 🌐 Endpoints Disponíveis

### OpenMind Direto
- `POST /analyze/` - Análise direta de imagens
- `POST /analyze/save-product/` - Salvar produto no banco

### CrewAI
- `GET/POST /analyze/crewai/` - Interface web para CrewAI
- `POST /api/crewai/analyze/` - API para análise com CrewAI

### Agnos
- `GET/POST /analyze/agnos/` - Interface web para Agnos
- `POST /api/agnos/analyze/` - API para análise com Agnos
- `POST /api/agnos/validate/` - API para validação com Agnos

## 📊 Comparação de Uso

| Aspecto | OpenMind Direto | CrewAI | Agnos |
|---------|----------------|--------|-------|
| **Complexidade** | Simples | Média | Alta |
| **Velocidade** | Rápida | Média | Mais lenta |
| **Agentes** | 0 | 2-4 | Múltiplos crews |
| **Workflows** | Linear | Sequencial | Complexos |
| **Estado** | Não mantém | Não mantém | Mantém |
| **Uso Ideal** | Análise rápida | Análise completa | Processos complexos |

## ✅ Vantagens da Arquitetura em 3 Níveis

1. **Flexibilidade**: Escolha o nível apropriado para cada caso
2. **Escalabilidade**: Pode adicionar mais crews/agentes conforme necessário
3. **Modularidade**: Cada nível pode ser usado independentemente
4. **Manutenibilidade**: Separação clara de responsabilidades
5. **Evolução**: Fácil adicionar novos níveis ou funcionalidades

## 🚀 Próximos Passos

1. [ ] Confirmar estrutura real do Agnos
2. [ ] Implementar integração completa do Agnos
3. [ ] Criar templates HTML para interfaces
4. [ ] Adicionar testes automatizados
5. [ ] Documentar workflows específicos
6. [ ] Implementar monitoramento e logging


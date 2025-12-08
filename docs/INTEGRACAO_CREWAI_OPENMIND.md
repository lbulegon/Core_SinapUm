# Integração CrewAI + OpenMind + Django (VitrineZap)

## 📋 Visão Geral

Este documento descreve como integrar o **CrewAI** (framework de agentes multi-agente) e o **OpenMind** (servidor de análise de imagens) no projeto **VitrineZap Django**.

## 🎯 Objetivos da Integração

1. **Agentes Especializados**: Criar agentes CrewAI para tarefas específicas:
   - Agente de Análise de Produtos
   - Agente de Enriquecimento de Dados
   - Agente de Validação de Qualidade
   - Agente de Geração de Anúncios

2. **Orquestração Inteligente**: CrewAI coordena múltiplos agentes trabalhando em conjunto

3. **Integração com OpenMind**: OpenMind continua responsável pela análise de imagens, mas agora é orquestrado pelo CrewAI

## 🏗️ Arquitetura Proposta

```
┌─────────────────────────────────────────────────────────────┐
│                    Django (VitrineZap)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Views / API Endpoints                       │  │
│  └─────────────────┬────────────────────────────────────┘  │
│                    │                                        │
│  ┌─────────────────▼────────────────────────────────────┐  │
│  │        CrewAI Orchestrator Service                   │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │  │
│  │  │ Agente   │  │ Agente   │  │ Agente   │          │  │
│  │  │ Análise  │  │ Enriquec │  │ Validação│          │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘          │  │
│  └───────┼─────────────┼──────────────┼─────────────────┘  │
│          │             │              │                     │
└──────────┼─────────────┼──────────────┼─────────────────────┘
           │             │              │
           └─────────────┴──────────────┘
                         │
           ┌─────────────▼──────────────┐
           │    OpenMind AI Server      │
           │  (Análise de Imagens)      │
           └────────────────────────────┘
```

## 📦 Instalação

### 1. Instalar CrewAI

```bash
pip install crewai crewai[tools]
```

### 2. Instalar ferramentas adicionais (opcional)

```bash
pip install langchain-openai langchain-community
```

### 3. Adicionar ao requirements.txt do Django

```bash
echo "crewai>=0.28.0" >> /root/SinapUm/requirements.txt
echo "langchain-openai>=0.1.0" >> /root/SinapUm/requirements.txt
```

## 🔧 Configuração

### 1. Configurar no settings.py

```python
# settings.py

# CrewAI Configuration
# IMPORTANTE: O CrewAI usa OpenMind.org como backend LLM!
# OpenMind.org oferece acesso a múltiplos modelos (OpenAI, Anthropic, Gemini, etc.)
# através de uma API unificada, usando a mesma chave do OpenMind AI.
CREWAI_CONFIG = {
    'default_llm': 'openmind',  # Usa OpenMind.org como backend
    'temperature': 0.7,
    'max_iterations': 3,
}

# OpenMind.org Configuration (para CrewAI LLM backend)
OPENMIND_ORG_BASE_URL = 'https://api.openmind.org/api/core/openai'
OPENMIND_ORG_API_KEY = OPENMIND_AI_KEY  # Usa a mesma chave!
OPENMIND_ORG_MODEL = 'gpt-4o'  # Pode ser: claude-3-opus, gemini-pro, etc.

# OpenMind AI (já existe)
OPENMIND_AI_URL = 'http://127.0.0.1:5000'
OPENMIND_AI_KEY = 'sua_chave_aqui'

# OpenAI/Anthropic (para CrewAI)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
```

## 👥 Agentes Criados

### 1. Agente de Análise de Produtos
- **Responsabilidade**: Analisar imagens usando OpenMind
- **Ferramentas**: Integração com OpenMind API
- **Output**: Dados extraídos no formato modelo.json

### 2. Agente de Enriquecimento de Dados
- **Responsabilidade**: Buscar informações adicionais (preços, reviews, etc.)
- **Ferramentas**: Web search, APIs externas
- **Output**: Dados enriquecidos

### 3. Agente de Validação
- **Responsabilidade**: Validar qualidade e completude dos dados
- **Ferramentas**: Validação de schema, checagem de consistência
- **Output**: Report de validação e dados corrigidos

### 4. Agente de Geração de Anúncios
- **Responsabilidade**: Criar textos para anúncios e posts
- **Ferramentas**: Templates, formatação
- **Output**: Anúncios prontos para WhatsApp/Marketplace

## 🔄 Fluxo de Trabalho (Crew)

```
1. Upload de Imagem(s)
   ↓
2. Agente Análise → OpenMind API → Extração de dados
   ↓
3. Agente Enriquecimento → Buscar preços/reviews → Dados completos
   ↓
4. Agente Validação → Verificar consistência → Dados validados
   ↓
5. Agente Geração → Criar anúncio → Anúncio pronto
   ↓
6. Salvar no PostgreSQL
```

## 📝 Exemplo de Implementação

Ver arquivo: `/root/SinapUm/app_sinapum/crewai_services.py`

## 🚀 Próximos Passos

1. [ ] Implementar agentes CrewAI
2. [ ] Integrar com OpenMind
3. [ ] Criar views Django para usar CrewAI
4. [ ] Testar fluxo completo
5. [ ] Documentar APIs e uso


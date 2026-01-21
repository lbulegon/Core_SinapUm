# Compat Report - SparkScore Service

**Data:** 2026-01-14  
**Versão Atual:** 1.0.0  
**Framework:** FastAPI 0.104.1

## 1. Inventário de Endpoints Existentes

### 1.1 Endpoints Públicos (Não Versionados)

#### `POST /sparkscore/analyze`
- **Descrição:** Análise completa: SparkScore + PPA
- **Payload Request:**
  ```json
  {
    "stimulus": {
      "text": "string",
      "image_url": "string (opcional)",
      "brand": "string (opcional)",
      "type": "string (opcional)"
    },
    "context": {
      "exposure_time": "number (opcional)",
      "exposure_count": "number (opcional)",
      "historical_engagement": "number (opcional)",
      "historical_conversion": "number (opcional)",
      "relevance_keywords": "array (opcional)"
    }
  }
  ```
- **Response (200):**
  ```json
  {
    "success": true,
    "result": {
      "sparkscore": 0.0-1.0,
      "ppa": {
        "status": "inativo|nascente|validado|ativo|cristalizado",
        "stage": "string|null",
        "confidence": 0.0-1.0,
        "profile": {
          "attraction": 0.0-1.0,
          "risk": 0.0-1.0,
          "noise": 0.0-1.0,
          "emotional_intensity": 0.0-1.0
        }
      },
      "orbital": {
        "orbital_dominante": 0-6,
        "orbitais_secundarios": [0-6],
        "grau_de_estabilidade": 0.0-1.0,
        "justificativa": "string",
        "impacto_no_sparkscore": 0.0-1.0,
        "scores_por_orbital": {0: float, 1: float, ...},
        "sinais_detectados": {...}
      },
      "semiotic": {...},
      "psycho": {...},
      "metric": {...},
      "motor_result": {...},
      "recommendations": ["string"]
    }
  }
  ```
- **Status Codes:** 200 (sucesso), 400 (stimulus obrigatório), 500 (erro interno)
- **Risco de Breaking Change:** ALTO - Endpoint principal, usado em produção

#### `POST /sparkscore/classify-orbital`
- **Descrição:** Classifica estímulo em orbital apenas
- **Payload Request:** Mesmo formato de `/analyze`
- **Response (200):**
  ```json
  {
    "success": true,
    "result": {
      "orbital_dominante": 0-6,
      "orbitais_secundarios": [0-6],
      "grau_de_estabilidade": 0.0-1.0,
      "justificativa": "string",
      "impacto_no_sparkscore": 0.0-1.0,
      "scores_por_orbital": {...},
      "sinais_detectados": {...}
    }
  }
  ```
- **Status Codes:** 200, 400, 500
- **Risco de Breaking Change:** MÉDIO

#### `POST /sparkscore/semiotic`
- **Descrição:** Análise semiótica apenas
- **Payload Request:** Mesmo formato de `/analyze`
- **Response (200):**
  ```json
  {
    "success": true,
    "result": {
      "peirce_type": "icon|index|symbol",
      "peirce_confidence": 0.0-1.0,
      "categories": ["string"],
      "mandela_effect": {
        "detected": boolean,
        "score": 0.0-1.0,
        "recurrence": 0.0-1.0,
        "potential": 0.0-1.0
      },
      "coherence_score": 0.0-1.0,
      "semiotic_analysis": {
        "icon_score": 0.0-1.0,
        "index_score": 0.0-1.0,
        "symbol_score": 0.0-1.0
      }
    }
  }
  ```
- **Status Codes:** 200, 500
- **Risco de Breaking Change:** BAIXO

#### `POST /sparkscore/psycho`
- **Descrição:** Análise psicológica apenas
- **Payload Request:** Mesmo formato de `/analyze`
- **Response (200):**
  ```json
  {
    "success": true,
    "result": {
      "attraction_score": 0.0-1.0,
      "attraction_factors": {...},
      "risk_score": 0.0-1.0,
      "risk_factors": {...},
      "noise_score": 0.0-1.0,
      "noise_factors": {...},
      "emotional_intensity": 0.0-1.0,
      "overall_psycho_score": 0.0-1.0
    }
  }
  ```
- **Status Codes:** 200, 500
- **Risco de Breaking Change:** BAIXO

#### `POST /sparkscore/metric`
- **Descrição:** Análise métrica apenas
- **Payload Request:** Mesmo formato de `/analyze`
- **Response (200):**
  ```json
  {
    "success": true,
    "result": {
      "engagement_probability": 0.0-1.0,
      "conversion_probability": 0.0-1.0,
      "quality_metrics": {
        "length_score": 0.0-1.0,
        "clarity_score": 0.0-1.0,
        "relevance_score": 0.0-1.0,
        "overall": 0.0-1.0
      },
      "overall_metric_score": 0.0-1.0
    }
  }
  ```
- **Status Codes:** 200, 500
- **Risco de Breaking Change:** BAIXO

#### `GET /sparkscore/orbitals`
- **Descrição:** Lista todos os orbitais disponíveis
- **Response (200):**
  ```json
  {
    "success": true,
    "orbitals": [
      {
        "id": 0-6,
        "name": "string",
        "description": "string",
        "function": "string",
        "motor": "string",
        "ppa_relation": "string|null"
      }
    ]
  }
  ```
- **Status Codes:** 200
- **Risco de Breaking Change:** BAIXO

#### `GET /sparkscore/health`
- **Descrição:** Health check
- **Response (200):**
  ```json
  {
    "status": "healthy",
    "service": "SparkScore"
  }
  ```
- **Status Codes:** 200
- **Risco de Breaking Change:** BAIXO

#### `GET /` (Root)
- **Descrição:** Health check geral
- **Response (200):**
  ```json
  {
    "service": "SparkScore - Sistema de Análise Psicológica e Semiótica",
    "status": "online",
    "version": "1.0.0"
  }
  ```
- **Status Codes:** 200
- **Risco de Breaking Change:** BAIXO

#### `GET /health`
- **Descrição:** Health check detalhado
- **Response (200):**
  ```json
  {
    "status": "healthy",
    "service": "SparkScore"
  }
  ```
- **Status Codes:** 200
- **Risco de Breaking Change:** BAIXO

## 2. Estrutura Interna Atual

### 2.1 Arquitetura
```
sparkscore_service/
├── app/
│   ├── main.py                    # FastAPI app entrypoint
│   ├── api/
│   │   └── routes.py              # Todas as rotas (sem versionamento)
│   ├── core/
│   │   ├── sparkscore_calculator.py  # Orquestrador principal
│   │   ├── orbital_classifier.py    # Classificação orbital
│   │   └── semiotic_normalizer.py   # Normalização semiótica
│   ├── agents/
│   │   ├── semiotic_agent.py        # Análise semiótica (Peirce)
│   │   ├── psycho_agent.py          # Análise psicológica
│   │   └── metric_agent.py          # Análise métrica
│   ├── motors/
│   │   ├── base_motor.py            # Classe base abstrata
│   │   ├── orbital_motor_factory.py # Factory de motores
│   │   ├── noise_filter_motor.py    # Orbital 0
│   │   ├── similarity_motor.py     # Orbital 1
│   │   ├── ppa_motor.py             # Orbital 2
│   │   ├── coherence_motor.py      # Orbital 3
│   │   ├── engagement_motor.py     # Orbital 4
│   │   ├── retention_motor.py      # Orbital 5
│   │   └── narrative_motor.py      # Orbital 6
│   └── models/
│       └── __init__.py              # Vazio (sem persistência ainda)
├── config/
│   └── orbitals.yaml               # Configuração dos orbitais
├── docs/                            # Vazio
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### 2.2 Dependências
- **FastAPI 0.104.1** - Framework web
- **SQLAlchemy 2.0.23** - ORM (não usado ainda)
- **PostgreSQL (psycopg2-binary)** - Banco (não configurado ainda)
- **Redis 5.0.1** - Cache (não usado ainda)
- **Pydantic 2.5.0** - Validação de dados
- **PyYAML 6.0.1** - Configuração YAML

### 2.3 Padrões Identificados
- **Sem versionamento de API:** Todas as rotas em `/sparkscore/*`
- **Sem persistência:** Nenhum modelo de banco de dados implementado
- **Sem testes:** Nenhum arquivo de teste encontrado
- **Sem feature flags:** Tudo sempre ativo
- **Sem logging estruturado:** Apenas exceptions básicas
- **Sem observability:** Sem métricas, tracing ou monitoring

## 3. Contratos Críticos (NÃO QUEBRAR)

### 3.1 Request/Response de `/sparkscore/analyze`
- **Campo obrigatório:** `stimulus` (deve existir e não ser vazio)
- **Formato de resposta:** `{"success": true, "result": {...}}`
- **Campos obrigatórios no result:**
  - `sparkscore` (float 0.0-1.0)
  - `ppa` (dict com `status`, `stage`, `confidence`, `profile`)
  - `orbital` (dict com `orbital_dominante`, `orbitais_secundarios`, etc.)
  - `semiotic`, `psycho`, `metric`, `motor_result`, `recommendations`

### 3.2 Classificação Orbital
- **Orbitais válidos:** 0-6 (inteiros)
- **Orbital 0:** Ruído
- **Orbital 1:** Reconhecimento
- **Orbital 2:** Expectativa (PPA nasce)
- **Orbital 3:** Alinhamento
- **Orbital 4:** Engajamento
- **Orbital 5:** Memória
- **Orbital 6:** Efeito Mandela

### 3.3 PPA (Perfil Psicológico de Atendimento)
- **Status válidos:** `inativo`, `nascente`, `validado`, `ativo`, `cristalizado`
- **Stage válidos:** `null`, `nasce`, `validado`, `ativado`, `cristalizado`
- **Confidence:** 0.0-1.0 (float)
- **Profile:** Sempre contém `attraction`, `risk`, `noise`, `emotional_intensity`

## 4. Riscos de Breaking Changes

### 4.1 Riscos ALTOS
1. **Alterar estrutura de resposta de `/sparkscore/analyze`**
   - **Impacto:** Clientes dependem do formato exato
   - **Mitigação:** Manter formato atual, adicionar campos opcionais

2. **Alterar lógica de cálculo de SparkScore**
   - **Impacto:** Scores mudariam para mesmos inputs
   - **Mitigação:** Manter algoritmo atual, adicionar versão de pipeline

3. **Alterar classificação orbital**
   - **Impacto:** Orbitais mudariam para mesmos estímulos
   - **Mitigação:** Manter algoritmo atual, adicionar versão de classificador

### 4.2 Riscos MÉDIOS
1. **Adicionar campos obrigatórios em requests**
   - **Mitigação:** Todos os novos campos devem ser opcionais

2. **Alterar status codes**
   - **Mitigação:** Manter status codes existentes, novos endpoints podem usar novos

3. **Alterar nomes de campos**
   - **Mitigação:** Nunca renomear, apenas adicionar novos campos

### 4.3 Riscos BAIXOS
1. **Adicionar novos endpoints**
   - **Mitigação:** Usar versionamento `/api/v1/*` ou `/api/v2/*`

2. **Adicionar campos opcionais em responses**
   - **Mitigação:** Campos opcionais não quebram clientes existentes

## 5. Dependências Internas

### 5.1 Fluxo de Análise Atual
```
POST /sparkscore/analyze
  ↓
calculate_sparkscore() (core/sparkscore_calculator.py)
  ↓
1. OrbitalClassifier.classify() → orbital_result
2. SemioticAgent.analyze() → semiotic_result
3. PsychoAgent.analyze() → psycho_result
4. MetricAgent.analyze() → metric_result
5. OrbitalMotorFactory.get_motor() → motor.process() → motor_result
6. _combine_scores() → sparkscore (float)
7. _calculate_ppa() → ppa (dict)
8. _generate_recommendations() → recommendations (list)
  ↓
Response: {"success": true, "result": {...}}
```

### 5.2 Dependências entre Componentes
- `SparkScoreCalculator` depende de:
  - `OrbitalClassifier`
  - `SemioticAgent`
  - `PsychoAgent`
  - `MetricAgent`
  - `OrbitalMotorFactory`
- `OrbitalClassifier` depende de:
  - `SemioticNormalizer`
  - `config/orbitals.yaml`
- Todos os `Motors` herdam de `BaseOrbitalMotor`

## 6. Integrações Externas

### 6.1 Nenhuma Identificada
- Não há chamadas HTTP externas
- Não há integração com banco de dados
- Não há integração com Redis
- Não há integração com serviços de autenticação/autorização

## 7. Observability Atual

### 7.1 Logging
- **Nível:** Apenas exceptions via FastAPI
- **Formato:** Não estruturado
- **Rastreabilidade:** Nenhuma (sem IDs de análise)

### 7.2 Métricas
- **Nenhuma métrica implementada**

### 7.3 Tracing
- **Nenhum tracing implementado**

## 8. Testes

### 8.1 Status
- **Testes unitários:** Não existem
- **Testes de integração:** Não existem
- **Testes de regressão:** Não existem
- **Testes de contrato:** Não existem

### 8.2 Cobertura
- **0% de cobertura de testes**

## 9. Documentação

### 9.1 Status
- **README.md:** Existe, mas precisa verificar conteúdo
- **API Docs:** FastAPI gera automaticamente em `/docs` e `/redoc`
- **Exemplos:** Não existem
- **Changelog:** Não existe

## 10. Conclusões e Recomendações

### 10.1 Pontos Fortes
- Arquitetura modular (agents, motors, core)
- Separação de responsabilidades clara
- Configuração externa (orbitals.yaml)

### 10.2 Pontos Fracos
- Sem versionamento de API
- Sem persistência de análises
- Sem testes
- Sem observability
- Sem feature flags
- Sem rastreabilidade (analysis_id)

### 10.3 Prioridades para Evolução
1. **CRÍTICO:** Adicionar testes de regressão antes de qualquer mudança
2. **ALTO:** Implementar versionamento de API
3. **ALTO:** Adicionar persistência com versionamento de pipeline
4. **MÉDIO:** Implementar feature flags
5. **MÉDIO:** Adicionar observability (logs estruturados, métricas)
6. **BAIXO:** Documentação e exemplos

### 10.4 Estratégia de Evolução
- **Fase 1:** Baseline e testes (Checkpoint 0)
- **Fase 2:** Estrutura interna sem quebrar API (Checkpoint 1)
- **Fase 3:** Pipeline versionado com pass-through (Checkpoint 2)
- **Fase 4:** Persistência e versionamento (Checkpoint 3)
- **Fase 5:** Novos endpoints versionados (Checkpoint 4)
- **Fase 6:** Orbitais evoluídos com flags (Checkpoint 5)
- **Fase 7:** PPA + CTA/CTR (Checkpoint 6)
- **Fase 8:** Insight Engine (Checkpoint 7)
- **Fase 9:** Observability (Checkpoint 8)
- **Fase 10:** Documentação (Checkpoint 9)


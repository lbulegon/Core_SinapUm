# SparkScore Service

## Sistema de Análise Psicológica e Semiótica

O SparkScore é um serviço de análise orbital de estímulos baseado na teoria de Peirce, fornecendo análise psicológica e semiótica completa.

### Descrição

Sistema de análise que combina:
- **Análise Psicológica**: Medição de atração, risco e ruído
- **Análise Semiótica**: Classificação baseada em teoria de Peirce (ícone, índice, símbolo)
- **Classificação Orbital**: 7 orbitais diferentes para classificação de estímulos
- **PPA (Ponto de Potencial de Atração)**: Análise de potencial de desenvolvimento

### Status do Serviço

- **Porta**: 8006
- **Framework**: FastAPI
- **Versão**: 1.0.0
- **Status**: ✅ Operacional

### Endpoints Disponíveis

#### 1. Health Check

**GET `/`**
- Descrição: Health check básico
- Resposta:
```json
{
  "service": "SparkScore - Sistema de Análise Psicológica e Semiótica",
  "status": "online",
  "version": "1.0.0"
}
```

**GET `/health`**
- Descrição: Health check detalhado
- Resposta:
```json
{
  "status": "healthy",
  "service": "SparkScore"
}
```

#### 2. Análise Completa

**POST `/sparkscore/analyze`**
- Descrição: Análise completa do estímulo (SparkScore + PPA + Orbital + Semiótica + Psicológica + Métricas)
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Retorna análise completa incluindo:
  - `sparkscore`: Score principal (0-1)
  - `ppa`: Status do PPA (inativo/ativo, stage, confidence, profile)
  - `orbital`: Classificação orbital (orbital dominante, orbitais secundários, grau de estabilidade)
  - `semiotic`: Análise semiótica (tipo Peirce, confidence, coerência)
  - `psycho`: Análise psicológica (atração, risco, ruído, intensidade emocional)
  - `metric`: Métricas (engajamento, conversão, qualidade)
  - `motor_result`: Resultado do motor de processamento
  - `recommendations`: Recomendações geradas

#### 3. Classificação Orbital

**POST `/sparkscore/classify-orbital`**
- Descrição: Classifica estímulo em orbital apenas
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```

#### 4. Análise Semiótica

**POST `/sparkscore/semiotic`**
- Descrição: Análise semiótica do estímulo
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Classifica tipo Peirce (icon, index, symbol) com confidence score

#### 5. Análise Psicológica

**POST `/sparkscore/psycho`**
- Descrição: Análise psicológica do estímulo
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Medição de atração, risco, ruído e intensidade emocional

#### 6. Análise Métrica

**POST `/sparkscore/metric`**
- Descrição: Análise métrica do estímulo
- Body:
```json
{
  "stimulus": {
    "text": "texto do estímulo"
  },
  "context": {}
}
```
- Resposta: Métricas de engajamento, conversão e qualidade

#### 7. Lista de Orbitais

**GET `/sparkscore/orbitals`**
- Descrição: Lista todos os orbitais disponíveis
- Resposta: Array com 7 orbitais (incluindo "Ruído", etc.)

#### 8. Documentação Interativa

**GET `/docs`**
- Descrição: Interface Swagger UI para documentação interativa
- Acesso: Navegador em `http://localhost:8006/docs`

**GET `/openapi.json`**
- Descrição: Especificação OpenAPI em JSON

### Exemplo de Uso

#### Análise Completa

```bash
curl -X POST http://localhost:8006/sparkscore/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "stimulus": {
      "text": "Exemplo de texto para análise"
    },
    "context": {}
  }'
```

#### Análise Semiótica

```bash
curl -X POST http://localhost:8006/sparkscore/semiotic \
  -H "Content-Type: application/json" \
  -d '{
    "stimulus": {
      "text": "Texto para análise semiótica"
    },
    "context": {}
  }'
```

#### Listar Orbitais

```bash
curl http://localhost:8006/sparkscore/orbitals
```

### Estrutura do Projeto

```
sparkscore_service/
├── app/
│   ├── agents/          # Agentes de análise
│   │   ├── semiotic_agent.py
│   │   ├── psycho_agent.py
│   │   └── metric_agent.py
│   ├── api/
│   │   └── routes.py    # Rotas da API
│   ├── core/
│   │   ├── sparkscore_calculator.py
│   │   └── orbital_classifier.py
│   ├── motors/          # Motores de processamento
│   ├── models/          # Modelos de dados
│   └── main.py          # Entrypoint FastAPI
├── config/              # Configurações
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

### Execução

#### Via Docker Compose (Recomendado)

O serviço está integrado ao `docker-compose.yml` principal do Core_SinapUm:

```bash
cd /root/Core_SinapUm
docker compose up -d sparkscore_service
```

#### Standalone

```bash
cd services/sparkscore_service
docker compose up -d
```

### Verificação de Status

```bash
# Verificar logs
docker compose logs sparkscore_service

# Verificar status
docker compose ps sparkscore_service

# Testar health check
curl http://localhost:8006/health
```

### Notas Técnicas

- **Orbitais Disponíveis**: 7 orbitais diferentes para classificação
- **Teoria de Peirce**: Classificação em ícone, índice ou símbolo
- **PPA**: Ponto de Potencial de Atração com análise de stages
- **Motores**: Sistema de motores para processamento e filtragem

### Integração

O serviço está integrado à rede `mcp_network` do Core_SinapUm e pode ser acessado por outros serviços através do nome `sparkscore_service` na porta 8006.

### Observações

- O healthcheck do Docker pode mostrar como "unhealthy" devido à ausência de `curl` no container, mas o serviço funciona corretamente
- A documentação interativa está disponível em `/docs` (Swagger UI)
- Todos os endpoints retornam JSON

---

## API v1 - Análise de Peças do Creative Engine

### Descrição

A API v1 foi criada especificamente para integração com o Creative Engine do VitrineZap. Ela utiliza um sistema de **orbitais** para análise multidimensional de peças criativas.

### Orbitais

Orbitais são camadas funcionais de análise que avaliam diferentes aspectos de uma peça:

#### Orbitais Ativos (MVP)
- **Semiótico**: Analisa CTA, coerência entre objetivo e texto, redundância
- **Emocional**: Analisa valência (positivo/negativo), urgência, tom emocional
- **Cognitivo**: Analisa densidade de palavras, clareza, adequação ao formato

#### Orbitais Placeholder (Futuro)
- **Narrativo**: Estrutura narrativa, arco de história (requer análise de sequência)
- **Cultural**: Adequação cultural, referências, sensibilidade (requer dataset cultural)
- **Ético**: Transparência, honestidade, responsabilidade (requer framework ético)
- **Psicanalítico**: Símbolos inconscientes, arquétipos (requer calibração de scores)
- **Temporal**: Timing, sazonalidade, urgência temporal (requer dados temporais)
- **Social**: Viralidade, compartilhamento, engajamento social (requer dados sociais)

### Endpoints v1

#### 1. Analisar Peça

**POST `/api/v1/analyze_piece`**

Analisa uma peça do Creative Engine usando todos os orbitais configurados.

**Request Body (Payload Padrão):**

```json
{
  "source": "vitrinezap_creative_engine",
  "source_version": "1.0.0",
  "piece": {
    "piece_id": "ce_2026_01_16_000123",
    "piece_type": "image",
    "created_at": "2026-01-16T14:32:10Z",
    "asset": {
      "asset_url": "https://cdn.vitrinezap.com/creatives/abc123.png",
      "asset_base64": null,
      "mime_type": "image/png",
      "width": 1080,
      "height": 1920
    },
    "text_overlay": "PROMOÇÃO SÓ HOJE",
    "caption": "Chame no WhatsApp e aproveite",
    "hashtags": ["#promoção", "#oferta", "#whatsapp"],
    "language": "pt-BR"
  },
  "brand": {
    "brand_id": "vitrinezap",
    "name": "VitrineZap",
    "tone": "direto, amigável",
    "palette": ["#FFC700", "#111111"],
    "category": "varejo_local"
  },
  "objective": {
    "primary_goal": "whatsapp_click",
    "cta_expected": true,
    "conversion_type": "conversa_whatsapp"
  },
  "audience": {
    "segment": "varejo_local",
    "persona": "consumidor_proximo",
    "awareness_level": "medio"
  },
  "distribution": {
    "channel": "whatsapp_status",
    "format": "story_vertical",
    "duration_seconds": null
  },
  "context": {
    "locale": "pt-BR",
    "region": "BR-RS",
    "time_context": "oferta_imediata",
    "campaign_id": "camp_janeiro_2026"
  },
  "options": {
    "return_placeholders": true,
    "explainability_level": "full",
    "store_analysis": true
  }
}
```

**Request Body (Mínimo):**

```json
{
  "source": "vitrinezap_creative_engine",
  "piece": {
    "piece_id": "ce_test_001",
    "piece_type": "image",
    "text_overlay": "PROMOÇÃO HOJE",
    "caption": "Chame no WhatsApp"
  },
  "objective": {
    "primary_goal": "whatsapp_click"
  },
  "distribution": {
    "channel": "whatsapp_status",
    "format": "story_vertical"
  }
}
```

**Response:**

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "piece_id": "ce_2026_01_16_000123",
  "pipeline_version": "1.0.0",
  "overall_score": 76.4,
  "orbitals": [
    {
      "orbital_id": "semiotic",
      "name": "Orbital Semiótico",
      "status": "active",
      "score": 80.0,
      "confidence": 0.68,
      "rationale": "CTA detectado (2 keywords). boa coerência entre goal e texto. baixa redundância",
      "top_features": ["cta_detected", "goal_coherence", "low_redundancy"],
      "raw_features": {
        "cta_detected": true,
        "cta_keywords_found": 2,
        "goal_match": 0.9,
        "redundancy_score": 0.2
      },
      "version": "1.0.0"
    },
    {
      "orbital_id": "emotional",
      "name": "Orbital Emocional",
      "status": "active",
      "score": 72.0,
      "confidence": 0.55,
      "rationale": "tom positivo moderado. urgência moderada. clareza emocional",
      "top_features": ["positive_tone", "urgency_detected"],
      "raw_features": {
        "positive_score": 0.3,
        "urgency_score": 0.4,
        "negative_score": 0.0
      },
      "version": "1.0.0"
    },
    {
      "orbital_id": "cognitive",
      "name": "Orbital Cognitivo",
      "status": "active",
      "score": 77.0,
      "confidence": 0.6,
      "rationale": "densidade adequada (8 palavras para story_vertical). objetivo claro refletido no texto",
      "top_features": ["optimal_density", "clear_goal"],
      "raw_features": {
        "word_count": 8,
        "density_score": 1.0,
        "goal_clarity": 0.8
      },
      "version": "1.0.0"
    },
    {
      "orbital_id": "narrative",
      "name": "Orbital Narrativo",
      "status": "placeholder",
      "score": null,
      "confidence": null,
      "rationale": "Orbital Narrativo mediria a estrutura narrativa da peça...",
      "top_features": [],
      "raw_features": {},
      "version": "0.1.0"
    }
  ],
  "insights": [
    {
      "level": "high",
      "title": "CTA bem alinhado ao canal",
      "description": "O objetivo é gerar cliques no WhatsApp e o CTA está presente no texto.",
      "recommendation": "Mantenha referência explícita ao WhatsApp."
    }
  ]
}
```

**Exemplo curl:**

```bash
curl -X POST http://localhost:8006/api/v1/analyze_piece \
  -H "Content-Type: application/json" \
  -d '{
    "source": "vitrinezap_creative_engine",
    "piece": {
      "piece_id": "ce_test_001",
      "piece_type": "image",
      "text_overlay": "PROMOÇÃO HOJE",
      "caption": "Chame no WhatsApp"
    },
    "objective": {
      "primary_goal": "whatsapp_click"
    },
    "distribution": {
      "channel": "whatsapp_status",
      "format": "story_vertical"
    }
  }'
```

#### 2. Recuperar Análise

**GET `/api/v1/analysis/{analysis_id}`**

Recupera uma análise anterior pelo ID.

**Response:**

```json
{
  "analysis_id": "550e8400-e29b-41d4-a716-446655440000",
  "piece_id": "ce_2026_01_16_000123",
  "pipeline_version": "1.0.0",
  "overall_score": 76.4,
  "orbitals": [...],
  "insights": [...],
  "created_at": "2026-01-16T14:32:10Z"
}
```

**Exemplo curl:**

```bash
curl http://localhost:8006/api/v1/analysis/550e8400-e29b-41d4-a716-446655440000
```

### Configuração de Orbitais

Os orbitais são configurados em `config/orbitals.yaml`:

```yaml
orbital_configs:
  semiotic:
    enabled: true
  emotional:
    enabled: true
  cognitive:
    enabled: true
  narrative:
    enabled: false  # Placeholder
  cultural:
    enabled: false  # Placeholder
  # ...
```

Para ativar um orbital placeholder, altere `enabled: true` no YAML.

### Estrutura de Orbitais

Cada orbital retorna:

- **orbital_id**: ID único (ex: "semiotic")
- **name**: Nome legível
- **status**: "active" (implementado), "placeholder" (futuro), "disabled" (erro)
- **score**: Score 0-100 (None para placeholders)
- **confidence**: Confiança 0-1 (None para placeholders)
- **rationale**: Explicação textual do resultado
- **top_features**: Lista de features mais relevantes
- **raw_features**: Features brutas extraídas
- **version**: Versão do orbital

### Insights

O pipeline gera insights automáticos baseados nos resultados:

- **level**: "low", "medium", "high"
- **title**: Título do insight
- **description**: Descrição do problema/oportunidade
- **recommendation**: Recomendação de ação

### Compatibilidade

- **Endpoints antigos**: Mantidos intactos em `/sparkscore/*`
- **Payload antigo**: Suportado (compatibilidade retroativa)
- **Payload Creative Engine**: Formato padrão recomendado

### Testes

Bateria de testes (unitários, casos de uso, integração, edge cases):

```bash
cd services/sparkscore_service

# Via Docker (recomendado)
docker compose -f ../../docker-compose.yml run --rm -v $(pwd):/app -e PYTHONPATH=/app sparkscore_service \
  sh -c "pip install -q pytest 'httpx<0.27' && pytest tests/ --ignore=tests/regression/ -v --tb=short"

# Localmente (com venv e deps instaladas)
pytest tests/ --ignore=tests/regression/ -v --tb=short
```

| Categoria | Pasta | Descrição |
|-----------|-------|-----------|
| Unit | `tests/unit/` | Orbitais CSV, Semiotic, BaseOrbital, Registry |
| Casos de uso | `tests/use_cases/` | Cenários reais (story WhatsApp, peça sem CTA, texto longo) |
| Integração | `tests/test_analyze_piece.py` | API `/api/v1/analyze_piece` |
| Edge cases | `tests/test_edge_cases.py` | Payloads extremos, formato legado |

Documentação de casos de uso: `docs/CASOS_DE_USO.md`

### Notas Técnicas

- **Armazenamento**: MVP usa armazenamento in-memory. Para produção, implementar persistência em banco de dados.
- **Pipeline Version**: Versão atual é `1.0.0`. Mudanças no pipeline incrementam a versão.
- **Orbitais Heurísticos**: Os orbitais ativos usam heurísticas simples. Podem ser refinados com ML no futuro.


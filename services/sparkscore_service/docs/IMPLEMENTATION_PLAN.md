# Implementation Plan - SparkScore Evolution

**Data de Início:** 2026-01-14  
**Versão Base:** 1.0.0  
**Versão Alvo:** 2.0.0 (com compatibilidade total com 1.0.0)

## Objetivo

Evoluir o SparkScore Service implementando:
- Orbitais evoluídos (Semiótico, Emocional, Cognitivo)
- PPA Engine aprimorado
- CTA/CTR/Conversion Heuristics
- Insight Engine
- Dashboard-ready APIs
- Persistência e versionamento
- Observability completa

**SEM QUEBRAR NADA DO QUE JÁ EXISTE.**

## Estratégia de Implementação

### Princípios
1. **Zero Breaking Changes:** Endpoints existentes mantêm comportamento exato
2. **Versionamento:** Novos recursos em `/api/v1/*` ou `/api/v2/*`
3. **Feature Flags:** Tudo novo protegido por flags
4. **Testes Primeiro:** Cada checkpoint tem testes de regressão
5. **Incremental:** Pequenos commits, checkpoints validados

## Checkpoints de Segurança

### Checkpoint 0 — Baseline ✅ (EM PROGRESSO)

**Objetivo:** Estabelecer linha de base e garantir que tudo funciona antes de mudanças.

**Tarefas:**
- [x] Inventário completo do código existente
- [x] Compat Report gerado
- [ ] Rodar serviço localmente
- [ ] Fazer chamadas de teste em todos os endpoints
- [ ] Salvar snapshots de request/response (golden files)
- [ ] Verificar se há testes existentes (rodar se houver)
- [ ] Documentar comportamento atual

**Critério de Aceite:**
- Serviço roda localmente sem erros
- Todos os endpoints respondem corretamente
- Snapshots salvos em `tests/regression/snapshots/`
- Documentação do comportamento atual completa

**Artefatos:**
- `tests/regression/snapshots/analyze_response.json`
- `tests/regression/snapshots/classify_orbital_response.json`
- `tests/regression/snapshots/semiotic_response.json`
- `tests/regression/snapshots/psycho_response.json`
- `tests/regression/snapshots/metric_response.json`
- `docs/BASELINE_BEHAVIOR.md`

---

### Checkpoint 1 — Estrutura Interna sem Alterar API Pública

**Objetivo:** Criar estrutura interna nova sem alterar comportamento externo.

**Tarefas:**
- [ ] Criar estrutura de diretórios:
  ```
  app/
    core/
      pipeline.py          # Novo: Pipeline versionado
      registry.py          # Novo: Registro de orbitais
      contracts.py         # Novo: Schemas estáveis
    orbitals/
      semiotic/            # Novo: Orbital Semiótico evoluído
      emotional/            # Novo: Orbital Emocional
      cognitive/            # Novo: Orbital Cognitivo
    engines/
      ppa_engine.py         # Novo: PPA Engine evoluído
      cta_engine.py         # Novo: CTA/CTR Engine
      insight_engine.py     # Novo: Insight Engine
    storage/
      repository.py         # Novo: Repositório de análises
      models.py             # Novo: Modelos SQLAlchemy
    utils/
      hashing.py            # Novo: Hash de conteúdo
      feature_flags.py      # Novo: Gerenciamento de flags
      logging.py            # Novo: Logging estruturado
  ```
- [ ] Criar `app/core/contracts.py` com schemas Pydantic estáveis
- [ ] Criar `app/utils/feature_flags.py` para gerenciar flags
- [ ] Criar `app/utils/logging.py` para logging estruturado
- [ ] Adicionar testes de regressão usando snapshots do Checkpoint 0
- [ ] Garantir que todos os testes passam

**Critério de Aceite:**
- Estrutura criada sem alterar código existente
- Todos os endpoints continuam funcionando exatamente como antes
- Testes de regressão passam (comparando com snapshots)
- Nenhum comportamento externo alterado

**Artefatos:**
- Estrutura de diretórios criada
- `app/core/contracts.py`
- `app/utils/feature_flags.py`
- `app/utils/logging.py`
- `tests/regression/test_endpoints.py` (testes de regressão)

---

### Checkpoint 2 — Core Score Engine (Modo Pass-Through)

**Objetivo:** Criar pipeline versionado que por padrão retorna exatamente o que já era retornado.

**Tarefas:**
- [ ] Criar `app/core/pipeline.py`:
  - Classe `ScorePipeline` com versão
  - Método `analyze()` que por padrão chama código antigo
  - Flag `SPARKSCORE_PIPELINE_V2=false` (padrão)
- [ ] Criar `app/core/registry.py`:
  - Registro de orbitais disponíveis
  - Sistema de plugins para orbitais
- [ ] Modificar `app/core/sparkscore_calculator.py`:
  - Adicionar opção de usar pipeline novo (se flag ativa)
  - Por padrão, usar código antigo (compatibilidade)
- [ ] Adicionar testes:
  - Teste que flag desativada = comportamento antigo
  - Teste que flag ativada = mesmo resultado (pass-through)
- [ ] Garantir que todos os testes de regressão passam

**Critério de Aceite:**
- Pipeline criado mas não usado por padrão
- Com flag desativada, comportamento idêntico ao atual
- Com flag ativada, resultado idêntico (pass-through)
- Todos os testes de regressão passam

**Artefatos:**
- `app/core/pipeline.py`
- `app/core/registry.py`
- Modificações em `app/core/sparkscore_calculator.py`
- `tests/unit/test_pipeline.py`

---

### Checkpoint 3 — Persistência e Versionamento

**Objetivo:** Adicionar persistência de análises sem alterar endpoints existentes.

**Tarefas:**
- [ ] Criar modelos SQLAlchemy em `app/storage/models.py`:
  ```python
  class Analysis:
    - id (UUID, primary key)
    - created_at (timestamp)
    - content_hash (string, indexado)
    - pipeline_version (string)
    - orbitals_enabled (JSON array)
    - stimulus (JSON)
    - context (JSON)
    - result (JSON)
    - scores (JSON)
    - insights (JSON, nullable)
    - raw_features (JSON, nullable)
  ```
- [ ] Criar `app/storage/repository.py`:
  - Métodos: `save()`, `get_by_id()`, `get_by_hash()`
  - Suporte a cache opcional (Redis se disponível)
- [ ] Criar `app/utils/hashing.py`:
  - Função para gerar hash de conteúdo (stimulus + context)
- [ ] Criar migrations (Alembic se necessário):
  - Tabela `analyses`
  - Índices em `content_hash` e `created_at`
- [ ] Integrar persistência no pipeline (opcional, via flag):
  - Flag `SPARKSCORE_PERSIST_ANALYSES=false` (padrão)
  - Se ativa, salva análise após processar
- [ ] Adicionar testes:
  - Teste de persistência
  - Teste de recuperação por ID
  - Teste de cache por hash
- [ ] Garantir que endpoints antigos não são afetados

**Critério de Aceite:**
- Modelos criados e migrations aplicadas
- Persistência funciona quando flag ativada
- Endpoints antigos não são afetados (flag desativada por padrão)
- Testes de persistência passam
- Testes de regressão continuam passando

**Artefatos:**
- `app/storage/models.py`
- `app/storage/repository.py`
- `app/utils/hashing.py`
- Migrations (se necessário)
- `tests/integration/test_storage.py`

---

### Checkpoint 4 — Endpoints Novos (Versionados)

**Objetivo:** Adicionar novos endpoints em `/api/v1/*` sem alterar endpoints antigos.

**Tarefas:**
- [ ] Criar `app/api/v1/`:
  - `routes.py` com novos endpoints
- [ ] Novos endpoints:
  - `POST /api/v1/analyze` - Análise com pipeline v2
  - `GET /api/v1/analysis/{analysis_id}` - Recuperar análise salva
  - `POST /api/v1/compare` - Comparação A/B
  - `POST /api/v1/insights` - Gerar insights
- [ ] Schemas Pydantic em `app/core/contracts.py`:
  - `AnalyzeRequestV1`
  - `AnalyzeResponseV1`
  - `AnalysisResponseV1`
  - `CompareRequestV1`
  - `CompareResponseV1`
  - `InsightsRequestV1`
  - `InsightsResponseV1`
- [ ] Integrar novos endpoints no `app/main.py`
- [ ] Adicionar testes:
  - Testes unitários dos novos endpoints
  - Testes de integração do fluxo completo
- [ ] Garantir que endpoints antigos continuam funcionando

**Critério de Aceite:**
- Novos endpoints funcionam em `/api/v1/*`
- Endpoints antigos em `/sparkscore/*` continuam funcionando
- Schemas validam corretamente
- Testes dos novos endpoints passam
- Testes de regressão dos endpoints antigos passam

**Artefatos:**
- `app/api/v1/routes.py`
- Schemas em `app/core/contracts.py`
- `tests/integration/test_v1_endpoints.py`

---

### Checkpoint 5 — Orbitais Evoluídos (Aditivos e com Flags)

**Objetivo:** Implementar orbitais Semiótico, Emocional e Cognitivo evoluídos, cada um com flag.

**Tarefas:**
- [ ] Criar `app/orbitals/semiotic/`:
  - `extractor.py` - Extração de features semióticas
  - `scorer.py` - Score 0-100
  - `explain.py` - Explicação textual
- [ ] Criar `app/orbitals/emotional/`:
  - `extractor.py` - Extração de features emocionais
  - `scorer.py` - Score 0-100
  - `explain.py` - Explicação textual
- [ ] Criar `app/orbitals/cognitive/`:
  - `extractor.py` - Extração de features cognitivas
  - `scorer.py` - Score 0-100
  - `explain.py` - Explicação textual
- [ ] Flags:
  - `ORBITAL_SEMIOTIC=true/false` (padrão: false)
  - `ORBITAL_EMOTIONAL=true/false` (padrão: false)
  - `ORBITAL_COGNITIVE=true/false` (padrão: false)
- [ ] Integrar orbitais no pipeline:
  - Se flag ativa, orbital é executado
  - Se flag inativa, orbital retorna `null` ou `disabled`
  - Schema sempre aceita `null` para compatibilidade
- [ ] Adicionar testes:
  - Testes unitários de cada orbital
  - Teste de flag desativada = null
  - Teste de flag ativada = score válido
- [ ] Garantir que comportamento antigo não é afetado

**Critério de Aceite:**
- Orbitais implementados e funcionais
- Flags controlam ativação/desativação
- Com flags desativadas, schema aceita `null`
- Com flags ativadas, orbitais retornam scores válidos
- Testes passam
- Endpoints antigos não são afetados

**Artefatos:**
- `app/orbitals/semiotic/*`
- `app/orbitals/emotional/*`
- `app/orbitals/cognitive/*`
- Modificações em `app/core/pipeline.py`
- `tests/unit/test_orbitals.py`

---

### Checkpoint 6 — PPA + CTA/CTR Engine

**Objetivo:** Implementar PPA Engine evoluído e CTA/CTR/Conversion Heuristics.

**Tarefas:**
- [ ] Criar `app/engines/ppa_engine.py`:
  - Heurísticas determinísticas (não "IA preta")
  - Output explicável:
    - `ppa_score` (0-100)
    - `frictions[]` (lista de fricções detectadas)
    - `boosters[]` (lista de boosters detectados)
  - Versionamento: `ppa_engine_version`
- [ ] Criar `app/engines/cta_engine.py`:
  - Regras claras para CTA/CTR:
    - Clareza do CTA
    - Fricção percebida
    - Saliência visual/textual
    - Coerência com contexto
    - Timing (momento ideal)
  - Output:
    - `cta_score` (0-100)
    - `ctr_estimate` (0-1)
    - `conversion_probability` (0-1)
    - `recommendations[]`
- [ ] Integrar engines no pipeline:
  - Flags: `PPA_ENGINE_V2=true/false`, `CTA_ENGINE_ENABLED=true/false`
  - Por padrão, usar PPA antigo (compatibilidade)
- [ ] Adicionar testes:
  - Testes unitários dos engines
  - Testes de heurísticas
  - Testes de explicabilidade
- [ ] Garantir que PPA antigo continua funcionando

**Critério de Aceite:**
- PPA Engine v2 implementado e explicável
- CTA/CTR Engine implementado
- Flags controlam ativação
- Com flags desativadas, comportamento antigo mantido
- Testes passam
- Outputs são explicáveis (não "caixa preta")

**Artefatos:**
- `app/engines/ppa_engine.py`
- `app/engines/cta_engine.py`
- Modificações em `app/core/pipeline.py`
- `tests/unit/test_engines.py`

---

### Checkpoint 7 — Insight Engine

**Objetivo:** Transformar scores em recomendações priorizadas e acionáveis.

**Tarefas:**
- [ ] Criar `app/engines/insight_engine.py`:
  - Transformar scores em insights:
    - `insight_id` (UUID)
    - `severity` (low/medium/high/critical)
    - `title` (string curta)
    - `rationale` (explicação)
    - `recommendation` (ação sugerida)
    - `expected_impact` (estimativa de melhoria)
  - Evitar "texto genérico": cada insight cita features e scores específicos
  - Priorização: insights mais impactantes primeiro
- [ ] Integrar no pipeline:
  - Flag: `INSIGHT_ENGINE_ENABLED=true/false` (padrão: false)
  - Se ativo, gera insights após análise
- [ ] Adicionar testes:
  - Teste de geração de insights
  - Teste de priorização
  - Teste de explicabilidade (não genérico)
- [ ] Garantir que insights são acionáveis

**Critério de Aceite:**
- Insight Engine gera insights relevantes
- Insights são específicos (não genéricos)
- Priorização funciona corretamente
- Testes passam
- Insights são acionáveis

**Artefatos:**
- `app/engines/insight_engine.py`
- Modificações em `app/core/pipeline.py`
- `tests/unit/test_insight_engine.py`

---

### Checkpoint 8 — Observability e Segurança

**Objetivo:** Adicionar logs estruturados, métricas e rastreabilidade.

**Tarefas:**
- [ ] Melhorar `app/utils/logging.py`:
  - Logs estruturados (JSON)
  - Cada análise tem `analysis_id` nos logs
  - `pipeline_version` nos logs
  - Níveis: DEBUG, INFO, WARNING, ERROR
- [ ] Adicionar métricas:
  - Latência por orbital
  - Taxa de erro por endpoint
  - Contador de análises
  - Histograma de scores
  - (Usar Prometheus se disponível, senão logs estruturados)
- [ ] Adicionar rastreabilidade:
  - `analysis_id` em todas as respostas (se pipeline v2)
  - `pipeline_version` em todas as respostas
  - Correlation ID em logs
- [ ] Rate limiting (se padrão existir no projeto):
  - Limitar requisições por IP/API key
- [ ] Sanitização de inputs:
  - Validar e sanitizar todos os inputs
  - Prevenir injection attacks
- [ ] Adicionar testes:
  - Teste de logs estruturados
  - Teste de métricas
  - Teste de rastreabilidade
- [ ] Garantir que performance não degrada

**Critério de Aceite:**
- Logs estruturados funcionam
- Métricas coletadas
- Rastreabilidade completa (analysis_id em tudo)
- Rate limiting implementado (se necessário)
- Sanitização de inputs funciona
- Testes passam
- Performance não degrada significativamente

**Artefatos:**
- Melhorias em `app/utils/logging.py`
- Sistema de métricas
- Modificações em `app/core/pipeline.py` (adicionar analysis_id)
- `tests/integration/test_observability.py`

---

### Checkpoint 9 — Documentação e Exemplos

**Objetivo:** Documentar tudo e fornecer exemplos de uso.

**Tarefas:**
- [ ] Atualizar `README.md`:
  - Como subir localmente
  - Como rodar testes
  - Como ativar feature flags
  - Exemplos de uso
- [ ] Criar `docs/API.md`:
  - Documentação completa da API
  - Exemplos curl para:
    - `POST /api/v1/analyze` (texto)
    - `POST /api/v1/analyze` (imagem, se suportar)
    - `POST /api/v1/analyze` (multimodal, se suportar)
    - `GET /api/v1/analysis/{analysis_id}`
    - `POST /api/v1/compare`
    - `POST /api/v1/insights`
  - Explicação de como ativar flags
- [ ] Criar `CHANGELOG.md`:
  - O que foi adicionado
  - Como ativar novos recursos
  - Notas de compatibilidade
  - Breaking changes (se houver, mas não deve haver)
- [ ] Criar `docs/ARCHITECTURE.md`:
  - Arquitetura do sistema
  - Fluxo de dados
  - Decisões de design
- [ ] Adicionar exemplos em `examples/`:
  - `analyze_text.py`
  - `analyze_image.py` (se suportar)
  - `compare_ab.py`
  - `get_insights.py`
- [ ] Garantir que documentação está completa e clara

**Critério de Aceite:**
- README completo e atualizado
- API documentada com exemplos
- CHANGELOG criado
- Exemplos funcionam
- Documentação permite uso sem contexto prévio

**Artefatos:**
- `README.md` atualizado
- `docs/API.md`
- `CHANGELOG.md`
- `docs/ARCHITECTURE.md`
- `examples/*.py`

---

## Ordem de Execução

1. **Checkpoint 0** → Baseline (NÃO PULAR)
2. **Checkpoint 1** → Estrutura interna
3. **Checkpoint 2** → Pipeline pass-through
4. **Checkpoint 3** → Persistência
5. **Checkpoint 4** → Endpoints novos
6. **Checkpoint 5** → Orbitais evoluídos
7. **Checkpoint 6** → PPA + CTA/CTR
8. **Checkpoint 7** → Insight Engine
9. **Checkpoint 8** → Observability
10. **Checkpoint 9** → Documentação

## Critérios de Aceite Final

- [ ] Todos os endpoints antigos respondem exatamente como antes (snapshot tests passam)
- [ ] Endpoints novos funcionam corretamente
- [ ] Flags podem desativar orbitais sem quebrar schema
- [ ] Análises persistem com versionamento e podem ser reobtidas por `analysis_id`
- [ ] Logs contêm `analysis_id` e `pipeline_version`
- [ ] Documentação permite uso sem contexto prévio
- [ ] Todos os testes passam
- [ ] Performance não degrada significativamente
- [ ] Zero breaking changes nos endpoints antigos

## Notas Importantes

1. **Nunca pular Checkpoint 0:** É a base de tudo
2. **Sempre rodar testes de regressão:** Após cada checkpoint
3. **Commits pequenos:** Um checkpoint pode ter vários commits
4. **Feature flags sempre desativadas por padrão:** Ativação manual
5. **Documentação em paralelo:** Não deixar para o final
6. **Testes primeiro:** TDD quando possível

## Próximos Passos

1. Completar Checkpoint 0 (baseline)
2. Revisar Compat Report e Implementation Plan
3. Começar Checkpoint 1 (estrutura interna)


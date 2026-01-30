# CI/CD - Testes automatizados

O Core_SinapUm utiliza **GitHub Actions** para executar testes automaticamente.

## Workflow

**Arquivo:** `.github/workflows/tests.yml`

**Triggers:** Push e Pull Request nas branches `main` e `master`

## Jobs

### 1. Unit Tests
- **SparkScore:** 41 testes (orbitais, pipeline, API)
- **ShopperBot:** 5 testes (intent, creative, recommendation)
- Serviços sobem via Docker Compose para execução isolada

### 2. Integration Tests
- **20+ testes** contra serviços reais (health, endpoints)
- Web, OpenMind, DDF, SparkScore, ShopperBot, MCP
- Executado após unit tests passarem

## Execução local

```bash
# Todos os testes
bash ./scripts/run_all_tests.sh all

# Só unit
bash ./scripts/run_all_tests.sh unit

# Só integração (exige docker compose up)
bash ./scripts/run_all_tests.sh integration
```

## Configuração CI

- Variáveis de ambiente mínimas para CI (POSTGRES_*)
- `.env` criado a partir de `.env.example` ou `.env.Original` quando ausente
- iFood e Chatwoot não são iniciados (não essenciais para testes)

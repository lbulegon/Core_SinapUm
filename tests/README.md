# Testes do Core_SinapUm

Bateria de testes cobrindo **todos os serviços ativos** do stack.

## Estrutura

```
tests/
├── services_config.py       # Portas e URLs dos serviços
├── unit/                    # PR5: testes unitários (não exigem serviços)
│   ├── test_a2a_planner.py  # PlannerAgent (fallback, padrões)
│   ├── test_a2a_executor.py # ExecutorAgent sync (mock)
│   ├── test_mcp_uri.py      # Parser/validação sinap://
│   └── test_adapters.py     # BaseAdapter e adapter concreto
├── integration/             # Testes que exigem serviços rodando
│   ├── test_acp_a2a_smoke.py # PR5: smoke ACP, A2A, Resources
│   ├── test_all_services_health.py
│   ├── test_mcp_full.py
│   └── ...
```

## Execução

### Pré-requisito: serviços rodando

```bash
cd /root/Core_SinapUm
docker compose up -d
```

### Rodar testes de integração

```bash
# Via Docker (recomendado - exige serviços rodando)
docker run --rm -v $(pwd):/app -w /app --network host -e TEST_BASE_HOST=localhost \
  python:3.11-slim bash -c "pip install -q pytest requests && pytest tests/integration/ -v"

# Ou via script
./scripts/run_all_tests.sh integration

# Local (se tiver pytest + requests)
pytest tests/integration/ -v
```

### Rodar testes unitários (não exigem serviços)

```bash
# A2A, MCP URI, adapters (PR5) — executar na raiz do projeto
pytest tests/unit/ -v --tb=short

# SparkScore
cd services/sparkscore_service && pytest tests/ --ignore=tests/regression/ -v

# ShopperBot
cd services/shopperbot_service && pytest tests/ -v
```

### Rodar tudo

```bash
./scripts/run_all_tests.sh all
```

## Serviços cobertos

| Serviço    | Porta | Testes                    |
|-----------|-------|---------------------------|
| Web (Django) | 5000 | health, root, admin       |
| OpenMind  | 8001  | health, root              |
| DDF       | 8005  | health, root, detect      |
| SparkScore| 8006  | health, analyze_piece, CSV|
| ShopperBot| 7030  | health, intent/classify   |
| MCP       | 7010  | health                    |
| iFood     | 7020  | health                    |

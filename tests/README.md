# Testes do Core_SinapUm

Bateria de testes cobrindo **todos os serviços ativos** do stack.

## Estrutura

```
tests/
├── services_config.py       # Portas e URLs dos serviços
├── integration/             # Testes que exigem serviços rodando
│   ├── test_all_services_health.py   # Health de: Web, OpenMind, DDF, SparkScore, ShopperBot
│   ├── test_sparkscore.py            # SparkScore: analyze_piece, orbital CSV
│   ├── test_openmind.py              # OpenMind: health
│   ├── test_ddf.py                   # DDF: health, detect
│   ├── test_shopperbot.py            # ShopperBot: health, intent classify
│   ├── test_web.py                   # Web Django: health, admin
│   └── test_mcp_ifood.py             # MCP, iFood: health
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

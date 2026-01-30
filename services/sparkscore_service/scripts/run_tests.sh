#!/bin/bash
# Roda a bateria de testes do SparkScore
# Uso (local): cd services/sparkscore_service && ./scripts/run_tests.sh
# Uso (Docker): docker compose run --rm -v $(pwd)/services/sparkscore_service:/app \
#   -e PYTHONPATH=/app sparkscore_service sh -c "pip install -q pytest 'httpx<0.27' && pytest tests/ --ignore=tests/regression/ -v --tb=short"

set -e
cd "$(dirname "$0")/.."

export PYTHONPATH="${PYTHONPATH:-$PWD}"

# Instalar deps de teste se necessário
pip install -q pytest 'httpx<0.27' 2>/dev/null || true

# Bateria completa (exclui regression que exige servidor rodando)
pytest tests/ --ignore=tests/regression/ -v --tb=short

#!/bin/bash
# Roda todos os testes do Core_SinapUm (unitários + integração)
# Uso:
#   ./scripts/run_all_tests.sh           # todos
#   ./scripts/run_all_tests.sh unit      # só unit (SparkScore, ShopperBot)
#   ./scripts/run_all_tests.sh integration  # só integração (exige docker compose up)

set -e
cd "$(dirname "$0")/.."

MODE="${1:-all}"

echo "=========================================="
echo "  TESTES CORE_SINAPUM"
echo "=========================================="

run_unit() {
    echo ""
    echo ">>> Unit: SparkScore"
    docker compose run --rm -v "$(pwd)/services/sparkscore_service:/app" -e PYTHONPATH=/app sparkscore_service \
        sh -c "pip install -q pytest 'httpx<0.27' && pytest tests/ --ignore=tests/regression/ -v --tb=short" 2>/dev/null || true

    echo ""
    echo ">>> Unit: ShopperBot"
    docker compose run --rm -v "$(pwd)/services/shopperbot_service:/app" -e PYTHONPATH=/app shopperbot_service \
        sh -c "pip install -q pytest && pytest tests/ -v --tb=short" 2>/dev/null || true
}

run_integration() {
    echo ""
    echo ">>> Integração: todos os serviços (exige docker compose up)"
    docker run --rm -v "$(pwd):/app" -w /app --network host -e TEST_BASE_HOST=localhost \
        python:3.11-slim bash -c "pip install -q pytest requests && pytest tests/integration/ -v --tb=short"
}

case "$MODE" in
    unit) run_unit ;;
    integration) run_integration ;;
    all)
        run_unit
        run_integration
        ;;
    *) echo "Uso: $0 [unit|integration|all]" && exit 2 ;;
esac

echo ""
echo "=========================================="
echo "  CONCLUÍDO"
echo "=========================================="

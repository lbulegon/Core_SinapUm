#!/bin/bash
# =============================================================================
# Run Event Consumers - Core_SinapUm
# =============================================================================
# Inicia os consumidores de eventos do Event Bus (Redis Streams).
# Uso: ./scripts/run_event_consumers.sh [core|evora|shopperbot|all]
# =============================================================================

set -e
CORE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$CORE_ROOT"

export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export PYTHONPATH="${CORE_ROOT}:${CORE_ROOT}/services/event_bus_service:${PYTHONPATH}"

run_core() {
    echo "Starting core_consumer..."
    python services/event_consumers/core_consumer.py
}

run_evora() {
    echo "Starting evora_consumer..."
    python services/event_consumers/evora_consumer.py
}

run_shopperbot() {
    echo "Starting shopperbot_consumer..."
    python services/event_consumers/shopperbot_consumer.py
}

case "${1:-all}" in
    core)    run_core ;;
    evora)   run_evora ;;
    shopperbot) run_shopperbot ;;
    all)
        run_core &
        run_evora &
        run_shopperbot &
        wait
        ;;
    *)
        echo "Uso: $0 [core|evora|shopperbot|all]"
        exit 1
        ;;
esac

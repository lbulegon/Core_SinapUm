#!/bin/bash
# Reconfigura webhooks das instâncias Evolution
# Uso: ./scripts/reconfigure_webhooks.sh [--restart]
#   --restart  Reinicia containers antes (pode demorar)

set -e
cd "$(dirname "$0")/.."

if [[ "$1" == "--restart" ]]; then
    echo "1. Reiniciando containers..."
    docker compose restart
    echo "2. Aguardando 30 segundos..."
    sleep 30
fi

echo "Executando reconfigure_webhooks --create-missing..."
docker compose exec web python manage.py reconfigure_webhooks --create-missing

echo "Concluído."

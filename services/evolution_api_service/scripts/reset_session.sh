#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ "${1:-}" != "--force" ]; then
  echo "Este script apaga volumes de sessao (instances, store). Use --force para confirmar."
  exit 1
fi

echo "Parando containers..."
docker compose down 2>/dev/null || docker compose -f docker-compose.yml -f docker-compose.build.yml down 2>/dev/null || true

echo "Removendo volumes de sessao..."
docker volume rm evolution_api_service_evolution_instances evolution_api_service_evolution_store 2>/dev/null || true
docker volume rm evolution_instances evolution_store 2>/dev/null || true

echo "Volumes removidos. Suba novamente com: ./scripts/up.sh ou ./scripts/up-build.sh"

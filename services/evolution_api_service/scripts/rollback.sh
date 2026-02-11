#!/bin/bash
set -e
cd "$(dirname "$0")/.."

if [ "${1:-}" != "--force" ]; then
  echo "Rollback: restaura docker-compose.yml do backup e sobe modo image. Use --force para confirmar."
  exit 1
fi

echo "Restaurando docker-compose.yml.bak..."
[ -f docker-compose.yml.bak ] && cp docker-compose.yml.bak docker-compose.yml || { echo "Backup nao encontrado."; exit 2; }

echo "Removendo override de build (se existir)..."
rm -f docker-compose.override.yml 2>/dev/null || true

echo "Subindo modo image..."
docker compose up -d

echo "Rollback concluido."

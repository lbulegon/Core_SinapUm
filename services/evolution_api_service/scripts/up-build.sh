#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Subindo Evolution API (modo build - patch 21/jan PR #2365)..."
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
echo "Aguardando healthy (ate 90s)..."
for i in $(seq 1 90); do
  if docker compose -f docker-compose.yml -f docker-compose.build.yml ps evolution-api 2>/dev/null | grep -q "healthy"; then
    echo "Evolution API healthy."
    exit 0
  fi
  sleep 1
done
echo "Aviso: healthcheck pode ainda estar em andamento."

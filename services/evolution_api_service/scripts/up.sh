#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Subindo Evolution API (modo image)..."
docker compose up -d
echo "Aguardando healthy (ate 60s)..."
for i in $(seq 1 60); do
  if docker compose ps evolution-api 2>/dev/null | grep -q "healthy"; then
    echo "Evolution API healthy."
    exit 0
  fi
  sleep 1
done
echo "Aviso: healthcheck pode ainda estar em andamento."

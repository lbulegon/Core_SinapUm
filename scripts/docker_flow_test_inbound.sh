#!/usr/bin/env bash
# Executa flow_test_ai_inbound **dentro** do contentor `web` (mesmo env/BD que o Gunicorn)
# e opcionalmente chama HTTP em localhost:5000.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker não encontrado no PATH."
  exit 1
fi

echo "Subindo db + openmind + web (se ainda não estiverem)…"
docker compose up -d db openmind web

echo "Esperando health do web…"
for i in $(seq 1 30); do
  if docker compose exec -T web curl -sf "http://127.0.0.1:5000/health" >/dev/null 2>&1 || \
     docker compose exec -T web curl -sf "http://127.0.0.1:5000/" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

export FEATURE_EVOLUTION_MULTI_TENANT="${FEATURE_EVOLUTION_MULTI_TENANT:-true}"
export FEATURE_OPENMIND_ENABLED="${FEATURE_OPENMIND_ENABLED:-true}"

echo "A correr flow_test_ai_inbound no contentor web (Gunicorn + env alinhados)…"
docker compose exec -T \
  -e FEATURE_EVOLUTION_MULTI_TENANT \
  -e FEATURE_OPENMIND_ENABLED \
  web sh -c 'cd /app && python manage.py flow_test_ai_inbound --url http://127.0.0.1:5000'

echo "Concluído."

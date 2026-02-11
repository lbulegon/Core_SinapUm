#!/bin/bash
# Script para rodar o WhatsApp Gateway Service
# Uso: ./run.sh [docker|local]

set -e
cd "$(dirname "$0")/../.."
MODE="${1:-docker}"

if [ "$MODE" = "docker" ]; then
  echo "Iniciando via Docker Compose..."
  docker compose up -d whatsapp_gateway_service
  echo "Servico iniciado. Logs: docker compose logs -f whatsapp_gateway_service"
elif [ "$MODE" = "local" ]; then
  if ! command -v node &>/dev/null; then
    echo "Node.js nao encontrado. Use: ./run.sh docker"
    exit 1
  fi
  cd services/whatsapp_gateway_service
  [ ! -d node_modules ] && npm install
  npm start
else
  echo "Uso: $0 [docker|local]"
  exit 1
fi

#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "Parando Evolution API..."
docker compose down
echo "Servicos parados."

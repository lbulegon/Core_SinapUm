#!/usr/bin/env bash
# Testa GET /api/v1/graph/status/ do MrFoo.
# Uso: MRFOO_BASE_URL=http://localhost:8000 ./scripts/test_mrfoo_graph_status.sh
# Ou: ./scripts/test_mrfoo_graph_status.sh  (usa MRFOO_BASE_URL do .env ou default)

set -e
BASE="${MRFOO_BASE_URL:-http://localhost:8000}"
TENANT="${1:-1}"
URL="${BASE}/api/v1/graph/status/"
echo "GET $URL (X-Tenant-ID: $TENANT)"
echo "---"
curl -s -w "\nHTTP_CODE:%{http_code}\n" "$URL" -H "X-Tenant-ID: $TENANT" | head -50

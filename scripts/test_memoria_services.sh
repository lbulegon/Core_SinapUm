#!/bin/bash
#
# Script para testar os serviços de Memória (WorldGraph + Vectorstore).
# Uso: ./scripts/test_memoria_services.sh
#      ./scripts/test_memoria_services.sh --up   # sobe os containers antes de testar
#
set -e

cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . .env && set +a

WORLDGRAPH_HTTP_PORT="${WORLDGRAPH_HTTP_PORT:-7474}"
VECTORSTORE_PORT="${VECTORSTORE_PORT:-8010}"
VECTORSTORE_URL="http://127.0.0.1:${VECTORSTORE_PORT}"
NEO4J_URL="http://127.0.0.1:${WORLDGRAPH_HTTP_PORT}"

DO_UP=""
for arg in "$@"; do
  case "$arg" in
    --up) DO_UP="1" ;;
    *) echo "Uso: $0 [--up]" && echo "  --up  sobe worldgraph_service e vectorstore_service antes de testar" && exit 2 ;;
  esac
done

echo "=========================================="
echo "  TESTE - Memória (WorldGraph + Vectorstore)"
echo "=========================================="
echo "Neo4j HTTP:    $NEO4J_URL"
echo "Vectorstore:   $VECTORSTORE_URL"
echo ""

if [ -n "$DO_UP" ]; then
  echo "▶️  Subindo worldgraph_service e vectorstore_service..."
  docker compose up -d worldgraph_service vectorstore_service
  echo "⏳ Aguardando 25s (Neo4j e Vectorstore iniciarem)..."
  sleep 25
  echo ""
fi

FAIL=0

# --- 1) WorldGraph (Neo4j) ---
echo "1) WorldGraph (Neo4j) - Health"
if curl -sS -m 10 -o /dev/null -w "%{http_code}" "$NEO4J_URL/" | grep -qE "200|301|302"; then
  echo "   ✅ Neo4j respondendo em $NEO4J_URL"
else
  echo "   ❌ FALHA: Neo4j não responde em $NEO4J_URL"
  echo "      Verifique: docker compose ps worldgraph_service"
  FAIL=1
fi
echo ""

# --- 2) Vectorstore - Health ---
echo "2) Vectorstore - GET /health"
HEALTH=$(curl -sS -m 10 "$VECTORSTORE_URL/health" 2>/dev/null || true)
if echo "$HEALTH" | grep -q '"ok":true'; then
  echo "   ✅ Vectorstore /health OK: $HEALTH"
else
  echo "   ❌ FALHA: Vectorstore não respondeu ou resposta inválida"
  echo "      Esperado: {\"ok\": true}  Recebido: $HEALTH"
  echo "      Verifique: docker compose ps vectorstore_service"
  FAIL=1
fi
echo ""

# --- 3) Vectorstore - Upsert ---
echo "3) Vectorstore - POST /upsert"
UPSERT_ID="test_$(date +%s)"
UPSERT_OUT=$(curl -sS -m 30 -X POST "$VECTORSTORE_URL/upsert" \
  -H "Content-Type: application/json" \
  -d "{\"id\":\"$UPSERT_ID\",\"text\":\"Pedido de teste aguardando aprovação do restaurante\"}" 2>/dev/null || true)
if echo "$UPSERT_OUT" | grep -q '"status":"ok"'; then
  echo "   ✅ Upsert OK (id=$UPSERT_ID)"
else
  echo "   ❌ FALHA: Upsert retornou: $UPSERT_OUT"
  FAIL=1
fi
echo ""

# --- 4) Vectorstore - Search ---
echo "4) Vectorstore - POST /search"
SEARCH_OUT=$(curl -sS -m 15 -X POST "$VECTORSTORE_URL/search" \
  -H "Content-Type: application/json" \
  -d '{"text":"pedido aguardando","k":5}' 2>/dev/null || true)
if echo "$SEARCH_OUT" | grep -q '"results"'; then
  echo "   ✅ Search OK: retornou lista de results"
  if echo "$SEARCH_OUT" | grep -q "$UPSERT_ID"; then
    echo "   ✅ O id do upsert ($UPSERT_ID) aparece nos resultados (busca semântica OK)"
  fi
  echo "   Resposta (resumo): $SEARCH_OUT"
else
  echo "   ❌ FALHA: Search retornou: $SEARCH_OUT"
  FAIL=1
fi
echo ""

# --- Resumo ---
echo "=========================================="
if [ "$FAIL" -eq 0 ]; then
  echo "  ✅ Todos os testes passaram!"
  echo ""
  echo "Próximos passos:"
  echo "  - Neo4j Browser: abra $NEO4J_URL e faça login (ex.: neo4j / neo4j12345)"
  echo "  - Popular grafo: docker exec -i mcp_sinapum_worldgraph cypher-shell -u neo4j -p neo4j12345 < services/worldgraph_service/seed/001_schema.cypher"
  echo "  - Ponte: use os 'id' retornados por POST /search no Neo4j: MATCH (n {id: \$id}) RETURN n"
else
  echo "  ❌ Alguns testes falharam. Verifique os containers:"
  echo "     docker ps -a | grep -E 'worldgraph|vectorstore'   # status (se docker compose ps travar, use este)"
  echo "     docker compose logs worldgraph_service vectorstore_service --tail=50"
  exit 1
fi
echo "=========================================="

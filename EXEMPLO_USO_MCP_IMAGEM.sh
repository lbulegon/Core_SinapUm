#!/bin/bash
# Exemplo prático: Usar MCP para analisar imagem com OpenMind

echo "🚀 Exemplo: Analisar Imagem via MCP"
echo "===================================="
echo ""

# API Key gerada pelo seed
API_KEY="Tm2Ox5yQ7jo5u9zkYMomRZwis0_aALEad4bNhlFVSFQ"

# URL do MCP Service
MCP_URL="http://localhost:7010/mcp/call"

echo "📋 1. Verificando se MCP Service está rodando..."
curl -s http://localhost:7010/health | jq . || echo "❌ MCP Service não está rodando!"

echo ""
echo "📋 2. Listando tools disponíveis..."
curl -s http://localhost:7010/mcp/tools | jq .

echo ""
echo "📋 3. Analisando imagem via MCP (formato legado)..."
curl -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "X-SINAPUM-KEY: $API_KEY" \
  -d '{
    "tool": "vitrinezap.analisar_produto",
    "version": "1.0.0",
    "input": {
      "source": "image",
      "image_url": "https://example.com/produto.jpg",
      "locale": "pt-BR",
      "mode": "fast"
    }
  }' | jq .

echo ""
echo "📋 4. Analisando imagem via MCP (formato MCP-aware)..."
curl -X POST "$MCP_URL" \
  -H "Content-Type: application/json" \
  -H "X-SINAPUM-KEY: $API_KEY" \
  -d '{
    "tool": "vitrinezap.analisar_produto",
    "context_pack": {
      "meta": {
        "actor": {"type": "user", "id": "user123"},
        "source": {"channel": "web", "conversation_id": "conv456"}
      },
      "task": {
        "name": "analisar_produto",
        "goal": "Extrair dados do produto da imagem"
      }
    },
    "input": {
      "source": "image",
      "image_url": "https://example.com/produto.jpg",
      "locale": "pt-BR",
      "mode": "fast"
    }
  }' | jq .

echo ""
echo "📋 5. Verificando logs no banco..."
docker exec mcp_sinapum_db psql -U mcp_user -d mcp_sinapum -c "SELECT request_id, trace_id, tool, ok, latency_ms, created_at FROM mcp_tool_call_log ORDER BY created_at DESC LIMIT 5;"

echo ""
echo "✅ Exemplo concluído!"


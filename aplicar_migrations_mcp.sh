#!/bin/bash
# Script para aplicar migrations do MCP Tool Registry

echo "🔍 Verificando containers..."
docker compose ps

echo ""
echo "⏳ Aguardando container web ficar saudável..."
sleep 30

echo ""
echo "📦 Aplicando migrations do app_mcp_tool_registry..."
docker exec mcp_sinapum_web python manage.py migrate app_mcp_tool_registry

echo ""
echo "✅ Verificando status das migrations..."
docker exec mcp_sinapum_web python manage.py showmigrations app_mcp_tool_registry

echo ""
echo "📊 Verificando tabelas no banco..."
docker exec mcp_sinapum_db psql -U mcp_user -d mcp_sinapum -c "\dt mcp_*"

echo ""
echo "🔍 Verificando estrutura da tabela mcp_tool_call_log..."
docker exec mcp_sinapum_db psql -U mcp_user -d mcp_sinapum -c "\d mcp_tool_call_log"

echo ""
echo "✅ Concluído!"


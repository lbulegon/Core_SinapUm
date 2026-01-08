#!/bin/bash
# Script de Monitoramento de Logs - Shadow Mode e Feature Flags
# Uso: ./scripts/monitor_shadow_logs.sh

echo "======================================================================"
echo "Monitoramento de Logs - WhatsApp Shadow Mode e Feature Flags"
echo "======================================================================"
echo ""
echo "Filtros ativos:"
echo "  - [SHADOW MODE] - Eventos gerados em shadow mode"
echo "  - [FEATURE_FLAG] - Verificações de feature flags"
echo "  - canonical - Eventos canônicos"
echo "  - webhook - Chamadas de webhook"
echo ""
echo "Pressione Ctrl+C para parar"
echo "======================================================================"
echo ""

# Monitorar logs em tempo real
docker logs -f mcp_sinapum_web 2>&1 | grep --line-buffered -E "\[SHADOW MODE\]|\[FEATURE_FLAG\]|canonical|webhook" --color=always

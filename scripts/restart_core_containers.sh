#!/bin/bash
#
# Reinicia containers do Core_SinapUm usando "docker restart" (não trava como "docker compose restart").
# Uso: ./scripts/restart_core_containers.sh           # todos
#      ./scripts/restart_core_containers.sh mcp_sinapum_vectorstore mcp_sinapum_worldgraph   # só alguns
#
set -e

cd "$(dirname "$0")/.."

# Timeouts para nenhum comando travar (script roda até o fim sem intervenção)
TIMEOUT_PS=10
TIMEOUT_RESTART=60
if command -v timeout >/dev/null 2>&1; then
  RUN_PS() { timeout "$TIMEOUT_PS" docker ps -a --format '{{.Names}}' 2>/dev/null; }
  RUN_RESTART() { timeout "$TIMEOUT_RESTART" docker restart "$1" 2>/dev/null; }
else
  RUN_PS() { docker ps -a --format '{{.Names}}' 2>/dev/null; }
  RUN_RESTART() { docker restart "$1" 2>/dev/null; }
fi

# Lista de container names do docker-compose.yml (ordem sugerida: db primeiro, depois dependentes)
ALL_CONTAINERS=(
  mcp_sinapum_db
  mcp_sinapum_openmind
  mcp_sinapum_web
  mcp_sinapum_mcp
  mcp_sinapum_ddf
  mcp_sinapum_ddf_redis
  mcp_sinapum_ddf_postgres
  mcp_sinapum_ifood
  mcp_sinapum_chatwoot_postgres
  mcp_sinapum_chatwoot_redis
  mcp_sinapum_chatwoot_rails
  mcp_sinapum_chatwoot_sidekiq
  mcp_sinapum_shopperbot
  mcp_sinapum_sparkscore
  core_sinapum_mlflow_postgres
  core_sinapum_mlflow
  mcp_sinapum_worldgraph
  mcp_sinapum_vectorstore
  mcp_sinapum_whatsapp_gateway
)

if [ $# -eq 0 ]; then
  CONTAINERS=("${ALL_CONTAINERS[@]}")
  echo "Reiniciando todos os ${#CONTAINERS[@]} containers do Core_SinapUm (docker restart)..."
else
  # Ignorar argumentos que não parecem nome de container (ex.: cd, /root/...)
  CONTAINERS=()
  for arg in "$@"; do
    if [[ "$arg" == mcp_sinapum_* ]] || [[ "$arg" == core_sinapum_* ]]; then
      CONTAINERS+=("$arg")
    else
      echo "⚠️  Ignorando argumento inválido (não é nome de container): $arg"
    fi
  done
  if [ ${#CONTAINERS[@]} -eq 0 ]; then
    echo "Nenhum container válido. Use nomes como mcp_sinapum_db ou core_sinapum_mlflow."
    exit 1
  fi
  echo "Reiniciando containers: ${CONTAINERS[*]}"
fi

for name in "${CONTAINERS[@]}"; do
  if RUN_PS | grep -qx "$name"; then
    echo "  restart $name"
    RUN_RESTART "$name" || echo "    ⚠️  falha ou timeout: $name"
  else
    echo "  (pulando $name - não existe)"
  fi
done

echo ""
echo "✅ Concluído. Status: docker ps -a --format \"table {{.Names}}\t{{.Status}}\" | grep mcp_sinapum"

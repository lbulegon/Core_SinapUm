#!/bin/bash
#
# Inicia os containers do Core_SinapUm um a um (docker start), na ordem de dependência.
# Não usa "docker compose up", evita travar com muitos containers de uma vez.
#
# Uso: ./scripts/start_core_containers.sh              # todos, um a um
#      ./scripts/start_core_containers.sh --no-wait    # sem pausa entre um e outro
#      ./scripts/start_core_containers.sh mcp_sinapum_db mcp_sinapum_vectorstore   # só alguns
#
set -e

cd "$(dirname "$0")/.."

TIMEOUT_PS=10
TIMEOUT_START=60
if command -v timeout >/dev/null 2>&1; then
  RUN_PS() { timeout "$TIMEOUT_PS" docker ps -a --format '{{.Names}}' 2>/dev/null; }
  RUN_PS_RUNNING() { timeout "$TIMEOUT_PS" docker ps --format '{{.Names}}' 2>/dev/null; }
  RUN_START() { timeout "$TIMEOUT_START" docker start "$1" 2>/dev/null; }
else
  RUN_PS() { docker ps -a --format '{{.Names}}' 2>/dev/null; }
  RUN_PS_RUNNING() { docker ps --format '{{.Names}}' 2>/dev/null; }
  RUN_START() { docker start "$1" 2>/dev/null; }
fi

# Ordem de subida: dependências primeiro (db, redis, postgres auxiliares), depois serviços
CONTAINERS_ORDER=(
  mcp_sinapum_db
  mcp_sinapum_ddf_redis
  mcp_sinapum_ddf_postgres
  mcp_sinapum_chatwoot_postgres
  mcp_sinapum_chatwoot_redis
  core_sinapum_mlflow_postgres
  mcp_sinapum_openmind
  mcp_sinapum_worldgraph
  mcp_sinapum_vectorstore
  mcp_sinapum_whatsapp_gateway
  mcp_sinapum_web
  mcp_sinapum_mcp
  mcp_sinapum_ddf
  mcp_sinapum_ifood
  mcp_sinapum_chatwoot_rails
  mcp_sinapum_chatwoot_sidekiq
  mcp_sinapum_shopperbot
  mcp_sinapum_sparkscore
  core_sinapum_mlflow
)

WAIT_BETWEEN=2
if [ "${1:-}" = "--no-wait" ]; then
  WAIT_BETWEEN=0
  shift
fi

if [ $# -eq 0 ]; then
  CONTAINERS=("${CONTAINERS_ORDER[@]}")
  echo "=========================================="
  echo "  Iniciando containers Core_SinapUm (um a um)"
  echo "=========================================="
  echo "Total: ${#CONTAINERS[@]} containers. Pausa entre cada: ${WAIT_BETWEEN}s"
  echo ""
else
  CONTAINERS=()
  for arg in "$@"; do
    if [[ "$arg" == mcp_sinapum_* ]] || [[ "$arg" == core_sinapum_* ]]; then
      CONTAINERS+=("$arg")
    else
      echo "⚠️  Ignorando argumento inválido: $arg"
    fi
  done
  if [ ${#CONTAINERS[@]} -eq 0 ]; then
    echo "Nenhum container válido. Use nomes como mcp_sinapum_db ou core_sinapum_mlflow."
    exit 1
  fi
  echo "Iniciando containers: ${CONTAINERS[*]}"
fi

for name in "${CONTAINERS[@]}"; do
  if RUN_PS | grep -qx "$name"; then
    if RUN_PS_RUNNING | grep -qx "$name"; then
      echo "  [já em execução] $name"
    else
      echo "  start $name"
      RUN_START "$name" || echo "    ⚠️  falha ou timeout: $name"
      [ "$WAIT_BETWEEN" -gt 0 ] && sleep "$WAIT_BETWEEN"
    fi
  else
    echo "  (pulando $name - container não existe; rode antes: docker compose up -d)"
  fi
done

echo ""
echo "✅ Concluído. Status:"
echo "   docker ps -a --format \"table {{.Names}}\t{{.Status}}\t{{.Ports}}\" | grep -E 'mcp_sinapum|core_sinapum'"

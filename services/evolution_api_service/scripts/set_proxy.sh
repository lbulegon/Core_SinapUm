#!/bin/bash
#
# Configura Proxy na Evolution API via endpoint /proxy/set/<instanceName>
#
# Requer:
#   EVOLUTION_API_KEY   (global)
#   INSTANCE_NAME       (ex: lbulegon)
#   PROXY_HOST
#   PROXY_PORT
#
# Opcional:
#   EVOLUTION_BASE_URL  (default: http://127.0.0.1:8004)
#   PROXY_PROTOCOL      (default: http)  # http|https|socks5 (conforme seu provedor)
#   PROXY_USERNAME
#   PROXY_PASSWORD
#
set -euo pipefail

BASE_URL="${EVOLUTION_BASE_URL:-http://127.0.0.1:8004}"
API_KEY="${EVOLUTION_API_KEY:?Defina EVOLUTION_API_KEY}"
INSTANCE_NAME="${INSTANCE_NAME:?Defina INSTANCE_NAME (ex: lbulegon)}"

PROXY_HOST="${PROXY_HOST:?Defina PROXY_HOST}"
PROXY_PORT="${PROXY_PORT:?Defina PROXY_PORT}"
PROXY_PROTOCOL="${PROXY_PROTOCOL:-http}"
PROXY_USERNAME="${PROXY_USERNAME:-}"
PROXY_PASSWORD="${PROXY_PASSWORD:-}"

echo "=========================================="
echo "  CONFIGURAR PROXY - EVOLUTION API"
echo "=========================================="
echo ""
echo "Base URL:   $BASE_URL"
echo "Instância:  $INSTANCE_NAME"
echo "Proxy:      $PROXY_PROTOCOL://$PROXY_HOST:$PROXY_PORT"
if [ -n "$PROXY_USERNAME" ]; then
  echo "Auth:       user informado (senha oculta)"
else
  echo "Auth:       sem usuário/senha"
fi
echo ""

payload=$(python3 - <<PY
import json, os
data = {
  "enabled": True,
  "host": os.environ["PROXY_HOST"],
  "port": str(os.environ["PROXY_PORT"]),
  "protocol": os.environ.get("PROXY_PROTOCOL","http"),
  "username": os.environ.get("PROXY_USERNAME",""),
  "password": os.environ.get("PROXY_PASSWORD",""),
}
print(json.dumps(data))
PY
)

echo "== 1) Aplicando proxy =="
curl -sS -m 30 -X POST "$BASE_URL/proxy/set/$INSTANCE_NAME" \
  -H "Content-Type: application/json" \
  -H "apikey: $API_KEY" \
  -H "Authorization: Bearer $API_KEY" \
  -d "$payload" | head -c 2000
echo -e "\n"

echo "== 2) Conferindo proxy aplicado =="
curl -sS -m 30 "$BASE_URL/proxy/find/$INSTANCE_NAME" \
  -H "apikey: $API_KEY" \
  -H "Authorization: Bearer $API_KEY" | head -c 2000
echo -e "\n"

echo "== 3) Restart da instância (recomendado) =="
curl -sS -m 30 -X POST "$BASE_URL/instance/restart/$INSTANCE_NAME" \
  -H "apikey: $API_KEY" \
  -H "Authorization: Bearer $API_KEY" | head -c 1200
echo -e "\n"

echo "Pronto. Agora rode:"
echo "  bash scripts/diagnose_qr.sh"


#!/bin/bash
# Smoke test: health + criar instancia + QR
set -e
cd "$(dirname "$0")/.."
[ -f .env ] && set -a && . .env && set +a

BASE_URL="${EVOLUTION_BASE_URL:-http://127.0.0.1:8004}"
API_KEY="${EVOLUTION_API_KEY:?Defina EVOLUTION_API_KEY no .env ou exporte}"
INSTANCE_ID="smoke-test-$(date +%s)"

echo "=========================================="
echo "  SMOKE TEST - Evolution API QR"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "Instance: $INSTANCE_ID"
echo ""

echo "1) docker compose ps"
docker compose ps 2>/dev/null || docker compose -f docker-compose.yml -f docker-compose.build.yml ps 2>/dev/null || true

echo ""
echo "2) Health check ($BASE_URL/)"
ok=0
for i in $(seq 1 30); do
  if curl -sS -m 5 "$BASE_URL/" >/dev/null 2>&1; then
    ok=1
    break
  fi
  sleep 1
done
if [ "$ok" != "1" ]; then
  echo "FALHA: Evolution nao respondeu. Verifique se o servico esta rodando."
  exit 2
fi
echo "   Health OK."

echo ""
echo "3) POST /instance/create + GET /instance/connect (solicitar QR)"
curl -sS -m 30 -X POST \
  -H "apikey: $API_KEY" -H "Authorization: Bearer $API_KEY" -H "Content-Type: application/json" \
  -d "{\"instanceName\":\"$INSTANCE_ID\",\"qrcode\":true,\"integration\":\"WHATSAPP-BAILEYS\"}" \
  "$BASE_URL/instance/create" >/dev/null || true

sleep 3
out=$(curl -sS -m 25 \
  -H "apikey: $API_KEY" -H "Authorization: Bearer $API_KEY" \
  "$BASE_URL/instance/connect/$INSTANCE_ID" || true)

echo ""
if echo "$out" | grep -qiE "base64|qrcode|pairing|code"; then
  echo "OK: Payload contem QR/pairing."
  echo "$out" | head -c 600
  echo ""
else
  echo "AVISO: Payload pode nao conter QR. Resposta:"
  echo "$out" | head -c 800
  echo ""
  echo "Diagnostico: docker compose logs evolution-api --tail 100"
  exit 1
fi

echo ""
echo "=========================================="
echo "  Smoke test concluido."
echo "=========================================="

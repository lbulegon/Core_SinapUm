#!/bin/bash
#
# Diagnóstico rápido de QR Code - Evolution API
#
# Uso:
#   bash scripts/diagnose_qr.sh
#   EVOLUTION_API_KEY=... EVOLUTION_BASE_URL=http://69.169.102.84:8004 bash scripts/diagnose_qr.sh
#
set -euo pipefail

# Por padrão, usar localhost (evita problemas de hairpin/NAT ao acessar o IP público a partir do próprio host).
BASE_URL="${EVOLUTION_BASE_URL:-http://127.0.0.1:8004}"
API_KEY="${EVOLUTION_API_KEY:-GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg}"

INSTANCE_ID="${INSTANCE_ID:-qrtest-$(date +%s)}"

echo "=========================================="
echo "  DIAGNÓSTICO QR - EVOLUTION API"
echo "=========================================="
echo ""
echo "Base URL:   $BASE_URL"
echo "Instance:   $INSTANCE_ID"
echo "API Key:    ${API_KEY:0:6}...${API_KEY: -4}"
echo ""

headers=(-H "apikey: ${API_KEY}" -H "Authorization: Bearer ${API_KEY}" -H "Content-Type: application/json")

echo "== 0) aguardando health (até 30s) =="
ok="0"
for i in {1..30}; do
  if curl -sS -m 3 "$BASE_URL/" >/dev/null 2>&1; then
    ok="1"
    break
  fi
  sleep 1
done
if [ "$ok" != "1" ]; then
  echo "❌ Evolution API não respondeu em $BASE_URL dentro de 30s."
  echo "   Dica: verifique com: docker compose ps && docker compose logs --tail 200 evolution-api"
  exit 2
fi
echo "✅ health OK"
echo ""

echo "== 1) Health (/) =="
curl -sS -m 10 "$BASE_URL/" | head -c 400 || true
echo -e "\n"

echo "== 2) fetchInstances =="
curl -sS -m 20 "${headers[@]}" "$BASE_URL/instance/fetchInstances" | head -c 2000 || true
echo -e "\n"

echo "== 3) create instance (qrcode=true) =="
curl -sS -m 30 -X POST "${headers[@]}" "$BASE_URL/instance/create" \
  -d "{\"instanceName\":\"$INSTANCE_ID\",\"qrcode\":true,\"integration\":\"WHATSAPP-BAILEYS\"}" | head -c 2000 || true
echo -e "\n"

echo "== 4) poll /instance/connect/<instance> (até 30s) =="
for i in {1..6}; do
  echo "--- tentativa $i/6 ---"
  out="$(curl -sS -m 20 "${headers[@]}" "$BASE_URL/instance/connect/$INSTANCE_ID" || true)"
  echo "$out" | head -c 600
  echo ""
  # se aparecer base64/qr, para
  if echo "$out" | grep -qiE "base64|qrcode|pairing"; then
    echo "✅ Parece que o QR/pairing apareceu na resposta acima."
    break
  fi
  sleep 5
done
echo ""

echo "== 5) logs do container (últimas 200 linhas, filtrando QR/decodeFrame/baileys) =="
if command -v docker >/dev/null 2>&1; then
  docker compose ps || true
  docker compose logs evolution-api --tail 200 2>/dev/null | \
    grep -i -E "decodeframe|baileys|qrcode|qr|pair|not logged in|connection errored|connection failure" | tail -120 || true
else
  echo "docker não encontrado; pulei logs."
fi

echo ""
echo "=========================================="
echo "  FIM DO DIAGNÓSTICO"
echo "=========================================="


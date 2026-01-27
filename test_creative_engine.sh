#!/bin/bash

# Script para testar o Creative Engine
# Uso: ./test_creative_engine.sh

BASE_URL="${BASE_URL:-http://localhost:5000}"
API_BASE="${BASE_URL}/api/creative-engine"

echo "=========================================="
echo "  Teste do Creative Engine"
echo "=========================================="
echo ""
echo "Base URL: $BASE_URL"
echo "API Base: $API_BASE"
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para fazer requisições
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${YELLOW}Testando: $description${NC}"
    echo "  Endpoint: $method $endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_BASE$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ Sucesso (HTTP $http_code)${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    else
        echo -e "  ${RED}✗ Erro (HTTP $http_code)${NC}"
        echo "$body"
    fi
    echo ""
}

# 1. Gerar Criativo
echo "1. Gerando novo criativo..."
CREATIVE_DATA='{
    "product_id": "prod_test_123",
    "shopper_id": "shopper_test_456",
    "channel": "whatsapp",
    "strategy": "test",
    "text_short": "Teste de criativo curto",
    "text_medium": "Este é um teste de criativo com texto médio para verificar o funcionamento do Creative Engine",
    "text_long": "Este é um teste completo de criativo com texto longo. O Creative Engine permite criar, adaptar e gerenciar criativos de forma eficiente."
}'

test_endpoint "POST" "/generate" "$CREATIVE_DATA" "Gerar Criativo"

# Extrair creative_id da resposta (se disponível)
CREATIVE_ID=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('creative_id', ''))" 2>/dev/null)
VARIANT_ID=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('variant_id', ''))" 2>/dev/null)

if [ -n "$CREATIVE_ID" ]; then
    echo -e "${GREEN}Creative ID gerado: $CREATIVE_ID${NC}"
    echo -e "${GREEN}Variant ID gerado: $VARIANT_ID${NC}"
    echo ""
    
    # 2. Gerar Variantes
    echo "2. Gerando variantes..."
    VARIANTS_DATA='{"count": 2}'
    test_endpoint "POST" "/$CREATIVE_ID/variants" "$VARIANTS_DATA" "Gerar Variantes"
    
    # 3. Adaptar Criativo
    if [ -n "$VARIANT_ID" ]; then
        echo "3. Adaptando criativo..."
        ADAPT_DATA='{
            "text_short": "Texto adaptado - versão melhorada",
            "text_medium": "Este criativo foi adaptado com sucesso através da API do Creative Engine"
        }'
        test_endpoint "POST" "/variants/$VARIANT_ID/adapt" "$ADAPT_DATA" "Adaptar Criativo"
    fi
    
    # 4. Registrar Performance
    echo "4. Registrando performance..."
    PERFORMANCE_DATA="{
        \"variant_id\": \"$VARIANT_ID\",
        \"creative_id\": \"$CREATIVE_ID\",
        \"product_id\": \"prod_test_123\",
        \"event_type\": \"view\",
        \"event_data\": {\"source\": \"test_script\"}
    }"
    test_endpoint "POST" "/performance" "$PERFORMANCE_DATA" "Registrar Performance"
    
    # 5. Recomendar Próximo
    echo "5. Obtendo recomendação..."
    test_endpoint "GET" "/recommend?product_id=prod_test_123&channel=whatsapp" "" "Recomendar Próximo Criativo"
else
    echo -e "${RED}Não foi possível obter Creative ID. Pulando testes dependentes.${NC}"
    echo ""
fi

# 6. Listar Criativos
echo "6. Listando criativos..."
test_endpoint "GET" "/list/" "" "Listar Criativos"

echo "=========================================="
echo "  Testes Concluídos"
echo "=========================================="
echo ""
echo "Para testar via interface web, acesse:"
echo "  $BASE_URL/api/creative-engine/test/"
echo ""

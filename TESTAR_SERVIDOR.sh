#!/bin/bash
# Script de Testes Automatizado para Servidor OpenMind AI (Linux/Mac)
# Testa todos os endpoints e funcionalidades do servidor

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
SERVER_IP="${1:-69.169.102.84}"
SERVER_USER="${2:-root}"
PORT="${3:-8000}"
BASE_URL="http://${SERVER_IP}:${PORT}"
TEST_IMAGE="${4:-}"

# Funções auxiliares
test_result() {
    local test_name="$1"
    local success="$2"
    local message="$3"
    
    if [ "$success" = "true" ]; then
        echo -e "${GREEN}[OK]${NC} $test_name"
        if [ -n "$message" ]; then
            echo -e "      ${message}"
        fi
    else
        echo -e "${RED}[ERRO]${NC} $test_name"
        if [ -n "$message" ]; then
            echo -e "      ${RED}${message}${NC}"
        fi
    fi
}

print_section() {
    echo ""
    echo "========================================"
    echo -e "${CYAN}$1${NC}"
    echo "========================================"
    echo ""
}

# Verificar dependências
if ! command -v curl &> /dev/null; then
    echo -e "${RED}[ERRO] curl nao encontrado. Instale curl primeiro.${NC}"
    exit 1
fi

# Cabeçalho
echo ""
echo "========================================"
echo -e "${CYAN}Testes do Servidor OpenMind AI${NC}"
echo "========================================"
echo "Servidor: $BASE_URL"
echo ""

# ============================================================================
# Teste 1: Conectividade Básica
# ============================================================================
print_section "1. Testes de Conectividade"

echo -e "${YELLOW}[TESTE]${NC} Verificando conectividade com servidor..."
if ping -c 1 -W 2 "$SERVER_IP" &> /dev/null; then
    test_result "Ping ao servidor" "true"
else
    test_result "Ping ao servidor" "false" "Servidor nao responde ao ping"
fi

# ============================================================================
# Teste 2: Status do Serviço
# ============================================================================
print_section "2. Status do Servico (systemd)"

if command -v ssh &> /dev/null; then
    echo -e "${YELLOW}[TESTE]${NC} Verificando status do servico no servidor..."
    SERVICE_STATUS=$(ssh -o ConnectTimeout=5 -o BatchMode=yes "${SERVER_USER}@${SERVER_IP}" "systemctl is-active openmind-ai" 2>/dev/null)
    if [ "$SERVICE_STATUS" = "active" ]; then
        test_result "Servico openmind-ai esta rodando" "true"
    else
        test_result "Servico openmind-ai esta rodando" "false" "Status: ${SERVICE_STATUS:-nao disponivel}"
    fi
else
    echo -e "${YELLOW}[AVISO]${NC} SSH nao disponivel. Pulando verificacao de servico."
fi

# ============================================================================
# Teste 3: Endpoints HTTP
# ============================================================================
print_section "3. Testes de Endpoints HTTP"

# Teste 3.1: Health Check
echo -e "${YELLOW}[TESTE]${NC} Testando endpoint /health..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${BASE_URL}/health" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    RESPONSE=$(curl -s --max-time 10 "${BASE_URL}/health" 2>/dev/null)
    test_result "Health Check (/health)" "true" "Status: $HTTP_CODE - $RESPONSE"
else
    test_result "Health Check (/health)" "false" "Status HTTP: ${HTTP_CODE:-timeout}"
fi

# Teste 3.2: Root Endpoint
echo -e "${YELLOW}[TESTE]${NC} Testando endpoint raiz (/)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${BASE_URL}/" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    test_result "Root Endpoint (/)" "true" "Status: $HTTP_CODE"
else
    test_result "Root Endpoint (/)" "false" "Status HTTP: ${HTTP_CODE:-timeout}"
fi

# Teste 3.3: Documentação
echo -e "${YELLOW}[TESTE]${NC} Testando endpoint de documentacao (/docs)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${BASE_URL}/docs" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    test_result "Documentacao (/docs)" "true" "Status: $HTTP_CODE - Acesse em: ${BASE_URL}/docs"
else
    test_result "Documentacao (/docs)" "false" "Status HTTP: ${HTTP_CODE:-timeout}"
fi

# Teste 3.4: OpenAPI JSON
echo -e "${YELLOW}[TESTE]${NC} Testando endpoint OpenAPI JSON (/openapi.json)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${BASE_URL}/openapi.json" 2>/dev/null)
if [ "$HTTP_CODE" = "200" ]; then
    ENDPOINTS=$(curl -s --max-time 10 "${BASE_URL}/openapi.json" 2>/dev/null | grep -o '"\/[^"]*"' | head -10 | tr '\n' ' ')
    test_result "OpenAPI JSON (/openapi.json)" "true" "Status: $HTTP_CODE - Endpoints: ${ENDPOINTS}"
else
    test_result "OpenAPI JSON (/openapi.json)" "false" "Status HTTP: ${HTTP_CODE:-timeout}"
fi

# ============================================================================
# Teste 4: Análise de Imagem
# ============================================================================
print_section "4. Testes de Analise de Imagem"

if [ -z "$TEST_IMAGE" ]; then
    echo -e "${YELLOW}[AVISO]${NC} Nenhuma imagem fornecida."
    echo "      Use: $0 $SERVER_IP $SERVER_USER $PORT /caminho/para/imagem.jpg"
    echo -e "${YELLOW}[AVISO]${NC} Pulando testes de analise de imagem..."
elif [ ! -f "$TEST_IMAGE" ]; then
    echo -e "${YELLOW}[AVISO]${NC} Imagem nao encontrada: $TEST_IMAGE"
    echo -e "${YELLOW}[AVISO]${NC} Pulando testes de analise de imagem..."
else
    echo -e "${YELLOW}[TESTE]${NC} Testando endpoint de analise de imagem..."
    HTTP_CODE=$(curl -s -o /tmp/analyze_response.json -w "%{http_code}" --max-time 30 \
        -X POST "${BASE_URL}/api/v1/analyze" \
        -F "image=@${TEST_IMAGE}" 2>/dev/null)
    
    if [ "$HTTP_CODE" = "200" ]; then
        RESPONSE=$(cat /tmp/analyze_response.json 2>/dev/null)
        test_result "Analise de Imagem (/api/v1/analyze)" "true" "Status: $HTTP_CODE"
        
        # Extrair informações da resposta JSON
        if command -v jq &> /dev/null; then
            SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false' 2>/dev/null)
            REQUEST_ID=$(echo "$RESPONSE" | jq -r '.request_id // "N/A"' 2>/dev/null)
            PROCESSING_TIME=$(echo "$RESPONSE" | jq -r '.processing_time_ms // "N/A"' 2>/dev/null)
            
            if [ "$SUCCESS" = "true" ]; then
                echo -e "      ${GREEN}Analise bem-sucedida!${NC}"
                echo "      Request ID: $REQUEST_ID"
                echo "      Tempo de processamento: ${PROCESSING_TIME}ms"
            fi
        else
            echo "      Resposta: $(echo "$RESPONSE" | head -c 100)"
        fi
        rm -f /tmp/analyze_response.json
    else
        ERROR_MSG=$(cat /tmp/analyze_response.json 2>/dev/null | head -c 200)
        test_result "Analise de Imagem (/api/v1/analyze)" "false" "Status HTTP: ${HTTP_CODE:-timeout} - ${ERROR_MSG}"
        rm -f /tmp/analyze_response.json
    fi
fi

# ============================================================================
# Teste 5: Performance
# ============================================================================
print_section "5. Testes de Performance"

echo -e "${YELLOW}[TESTE]${NC} Medindo tempo de resposta do health check..."
TIMES=()
for i in {1..5}; do
    TIME=$(curl -s -o /dev/null -w "%{time_total}" --max-time 5 "${BASE_URL}/health" 2>/dev/null)
    if [ -n "$TIME" ] && [ "$TIME" != "0.000" ]; then
        TIMES+=($(echo "$TIME * 1000" | bc 2>/dev/null || echo "0"))
    fi
done

if [ ${#TIMES[@]} -gt 0 ]; then
    SUM=0
    for time in "${TIMES[@]}"; do
        SUM=$(echo "$SUM + $time" | bc 2>/dev/null || echo "$SUM")
    done
    AVG=$(echo "scale=2; $SUM / ${#TIMES[@]}" | bc 2>/dev/null || echo "0")
    MIN=$(printf '%s\n' "${TIMES[@]}" | sort -n | head -1)
    MAX=$(printf '%s\n' "${TIMES[@]}" | sort -rn | head -1)
    test_result "Tempo medio de resposta" "true" "${AVG}ms (min: ${MIN}ms, max: ${MAX}ms)"
else
    test_result "Tempo medio de resposta" "false" "Nao foi possivel medir"
fi

# ============================================================================
# Resumo Final
# ============================================================================
print_section "Resumo dos Testes"

echo -e "${GREEN}Testes concluidos!${NC}"
echo ""
echo -e "${CYAN}Proximos passos:${NC}"
echo "  1. Acesse a documentacao interativa: $BASE_URL/docs"
echo "  2. Verifique os logs: ssh ${SERVER_USER}@${SERVER_IP} 'journalctl -u openmind-ai -f'"
echo "  3. Veja logs estruturados: ssh ${SERVER_USER}@${SERVER_IP} 'tail -f /var/log/openmind-ai/app.log'"
echo ""


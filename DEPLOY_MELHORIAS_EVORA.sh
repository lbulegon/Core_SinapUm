#!/bin/bash
# Script de Deploy para Melhorias do Padrão Évora
# Atualiza código de análise de imagens no servidor

set -e

SERVER_IP="${1:-69.169.102.84}"
SERVER_USER="${2:-root}"
APP_PATH="/opt/openmind-ai/app"

echo "========================================"
echo "Deploy Melhorias Padrão Évora"
echo "========================================"
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Fazer backup
echo -e "${YELLOW}[1/6] Fazendo backup do código atual...${NC}"
ssh "${SERVER_USER}@${SERVER_IP}" "
    cd /opt/openmind-ai
    BACKUP_DIR=\"backups/backup_evora_\$(date +%Y%m%d_%H%M%S)\"
    mkdir -p \"\$BACKUP_DIR\"
    cp -r app \"\$BACKUP_DIR/\"
    echo \"Backup criado em: \$BACKUP_DIR\"
"

# 2. Copiar novos arquivos
echo -e "${YELLOW}[2/6] Copiando novos arquivos...${NC}"
scp app/core/image_analyzer_evora.py "${SERVER_USER}@${SERVER_IP}:${APP_PATH}/core/"
scp app/api/v1/endpoints/analyze_evora.py "${SERVER_USER}@${SERVER_IP}:${APP_PATH}/api/v1/endpoints/"

# 3. Verificar se precisa atualizar main.py ou routes
echo -e "${YELLOW}[3/6] Verificando rotas...${NC}"
ssh "${SERVER_USER}@${SERVER_IP}" "
    cd ${APP_PATH}
    # Verificar se analyze_evora.py precisa ser importado no main
    if grep -q 'from app.api.v1.endpoints import analyze' main.py; then
        echo 'Import encontrado - pode precisar atualizar para analyze_evora'
    fi
"

# 4. Reiniciar serviço
echo -e "${YELLOW}[4/6] Reiniciando serviço...${NC}"
ssh "${SERVER_USER}@${SERVER_IP}" "
    systemctl restart openmind-ai
    sleep 3
    if systemctl is-active --quiet openmind-ai; then
        echo 'Serviço reiniciado com sucesso'
    else
        echo 'ERRO: Serviço não está rodando'
        systemctl status openmind-ai --no-pager -l
        exit 1
    fi
"

# 5. Verificar logs
echo -e "${YELLOW}[5/6] Verificando logs...${NC}"
ssh "${SERVER_USER}@${SERVER_IP}" "
    journalctl -u openmind-ai -n 20 --no-pager | tail -10
"

# 6. Teste rápido
echo -e "${YELLOW}[6/6] Testando endpoint...${NC}"
ssh "${SERVER_USER}@${SERVER_IP}" "
    curl -s http://localhost:8000/health | head -3
"

echo ""
echo -e "${GREEN}Deploy concluído!${NC}"
echo ""
echo "Próximos passos:"
echo "  1. Testar análise com: .\OBTER_ANALISE_JSON_SIMPLES.ps1 -Imagem 'img\coca.jpg' -ApiKey 'sua_key'"
echo "  2. Verificar logs: ssh ${SERVER_USER}@${SERVER_IP} 'journalctl -u openmind-ai -f'"
echo "  3. Verificar se JSON retorna dados detalhados agora"
echo ""



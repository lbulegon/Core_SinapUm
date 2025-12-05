#!/bin/bash
# Script de Deploy Rápido para SinapUm
# Executa todos os passos necessários para atualizar o servidor

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configurações
APP_NAME="openmind-ai"
APP_PATH="/opt/openmind-ai"
LOG_DIR="/var/log/openmind-ai"
SERVICE_NAME="openmind-ai"
BACKUP_DIR="$APP_PATH/backups"

echo -e "${CYAN}🚀 Script de Deploy Rápido - OpenMind AI${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${YELLOW}⚠️  Executando sem privilégios root. Alguns comandos podem falhar.${NC}"
    echo ""
fi

# 1. Criar backup
echo -e "${CYAN}[1/7] Criando backup do código atual...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"
if [ -d "$APP_PATH/app" ]; then
    cp -r "$APP_PATH/app" "$BACKUP_PATH/" 2>/dev/null || true
    echo -e "${GREEN}✅ Backup criado em: $BACKUP_PATH${NC}"
else
    echo -e "${YELLOW}⚠️  Diretório app não encontrado. Pulando backup.${NC}"
fi

# 2. Criar estrutura de diretórios
echo -e "${CYAN}[2/7] Criando estrutura de diretórios...${NC}"
mkdir -p "$APP_PATH/app"
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"
echo -e "${GREEN}✅ Estrutura criada${NC}"

# 3. Atualizar código (assumindo que os arquivos já estão no servidor)
# Se você copiar via SCP antes de executar este script, os arquivos já estarão aqui
echo -e "${CYAN}[3/7] Verificando arquivos...${NC}"
if [ ! -f "$APP_PATH/requirements.txt" ]; then
    echo -e "${RED}❌ Erro: requirements.txt não encontrado em $APP_PATH${NC}"
    echo -e "${YELLOW}  Certifique-se de copiar os arquivos antes de executar este script${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Arquivos encontrados${NC}"

# 4. Ativar ambiente virtual e instalar dependências
echo -e "${CYAN}[4/7] Instalando dependências Python...${NC}"
cd "$APP_PATH"

if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}  Criando ambiente virtual...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

pip install --upgrade pip -q
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependências instaladas${NC}"

# 5. Aplicar permissões
echo -e "${CYAN}[5/7] Aplicando permissões...${NC}"
chmod -R 755 "$APP_PATH/app"
chmod 644 "$APP_PATH/promtail-config.yml" 2>/dev/null || true
chmod 644 "$APP_PATH/requirements.txt" 2>/dev/null || true
echo -e "${GREEN}✅ Permissões aplicadas${NC}"

# 6. Reiniciar serviço
echo -e "${CYAN}[6/7] Reiniciando serviço $SERVICE_NAME...${NC}"
if systemctl is-active --quiet "$SERVICE_NAME"; then
    systemctl restart "$SERVICE_NAME"
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Serviço reiniciado com sucesso${NC}"
    else
        echo -e "${RED}❌ Erro: Serviço não está rodando após reinício${NC}"
        systemctl status "$SERVICE_NAME" --no-pager -l
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Serviço não está rodando. Iniciando...${NC}"
    systemctl start "$SERVICE_NAME" || true
fi

# 7. Verificar saúde
echo -e "${CYAN}[7/7] Verificando saúde do serviço...${NC}"
sleep 2

# Verificar status do serviço
if systemctl is-active --quiet "$SERVICE_NAME"; then
    echo -e "${GREEN}✅ Serviço está rodando${NC}"
else
    echo -e "${RED}❌ Serviço não está rodando${NC}"
    systemctl status "$SERVICE_NAME" --no-pager -l
    exit 1
fi

# Verificar se o diretório de logs foi criado
if [ -d "$LOG_DIR" ]; then
    echo -e "${GREEN}✅ Diretório de logs criado: $LOG_DIR${NC}"
else
    echo -e "${YELLOW}⚠️  Diretório de logs não encontrado${NC}"
fi

# Mostrar logs recentes
echo ""
echo -e "${CYAN}📋 Últimas linhas dos logs do sistema:${NC}"
journalctl -u "$SERVICE_NAME" -n 10 --no-pager || true

# Resumo
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}✅ Deploy concluído!${NC}"
echo ""
echo "Próximos passos:"
echo "  1. Ver logs: journalctl -u $SERVICE_NAME -f"
echo "  2. Ver logs estruturados: tail -f $LOG_DIR/app.log"
echo "  3. Configurar Promtail com: $APP_PATH/promtail-config.yml"
echo "  4. Verificar logs JSON: cat $LOG_DIR/app.log | jq ."
echo ""

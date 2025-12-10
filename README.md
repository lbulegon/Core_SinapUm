# 🚀 SinapUm - Servidor VPS OpenMind AI

Servidor VPS Ubuntu dedicado para hospedar o **OpenMind AI Server**, uma aplicação FastAPI que oferece análise inteligente de imagens de produtos usando modelos de IA.

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Informações do Servidor](#-informações-do-servidor)
- [Arquitetura do Sistema](#-arquitetura-do-sistema)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação Inicial](#-instalação-inicial)
- [Configuração](#-configuração)
- [Deploy](#-deploy)
- [Monitoramento e Logs](#-monitoramento-e-logs)
- [Integração Grafana/Loki](#-integração-grafanaloki)
- [Comandos Úteis](#-comandos-úteis)
- [Troubleshooting](#-troubleshooting)
- [Manutenção](#-manutenção)

---

## 🎯 Visão Geral

O **SinapUm** é um servidor VPS Ubuntu configurado para executar o **OpenMind AI Server**, que fornece endpoints REST para:

- 📸 **Análise de imagens de produtos** - Extração de informações estruturadas de imagens
- 🔍 **Reconhecimento de objetos** - Identificação de produtos em imagens
- 📊 **Métricas e Logging** - Sistema completo de observabilidade com Grafana/Loki
- 🔐 **API Segura** - Autenticação via API keys

### Tecnologias Principais

- **Python 3.10+** - Linguagem principal
- **FastAPI** - Framework web assíncrono
- **OpenMind.org API** - Modelo de IA para análise de imagens
- **Grafana** - Visualização de dados e dashboards
- **Loki** - Agregação de logs
- **Promtail** - Coleta de logs
- **Prometheus** - Métricas (futuro)
- **systemd** - Gerenciamento de serviços

---

## 🌐 Informações do Servidor

### Detalhes Técnicos

- **IP Público**: `69.169.102.84`
- **Sistema Operacional**: Ubuntu Server
- **Usuário**: `root`
- **Caminho da Aplicação**: `/root/SinapUm`
- **Porta Django**: `80` (servidor principal)
- **Porta OpenMind AI**: `8000` (API de análise de imagens)
- **Framework**: Django

### Acesso SSH

```bash
ssh root@69.169.102.84
```

### Estrutura de Diretórios

```
/root/SinapUm/                 # Diretório principal do projeto Django
├── app_sinapum/               # App principal Django
│   ├── migrations/            # Migrações do banco de dados
│   ├── templates/             # Templates HTML
│   ├── models.py              # Models do Django
│   ├── views.py               # Views/Controllers
│   ├── admin.py               # Configuração do Admin
│   ├── services.py            # Serviços e lógica de negócio
│   └── utils.py               # Utilitários
├── setup/                     # Configurações do projeto Django
│   ├── settings.py            # Configurações principais
│   ├── urls.py                # URLs principais
│   └── wsgi.py                # WSGI config
├── media/                     # Arquivos de mídia (upload)
│   └── uploads/               # Imagens enviadas
├── static/                    # Arquivos estáticos
├── docs/                      # Documentação do projeto
├── venv/ ou .venv/            # Ambiente virtual Python
├── manage.py                  # Script de gerenciamento Django
├── db.sqlite3                 # Banco de dados SQLite (desenvolvimento)
├── requirements.txt           # Dependências Python (Django, Gunicorn, etc.)
└── README.md                  # Este arquivo

/root/openmind_ws/             # Workspace do projeto OpenMind (OM1)
└── OM1/                       # Projeto OpenMind OM1 - Runtime AI modular
    ├── src/                   # Código fonte principal
    ├── config/                # Arquivos de configuração
    ├── tests/                 # Testes automatizados
    ├── docs/                  # Documentação do projeto
    ├── scripts/               # Scripts auxiliares
    ├── gazebo/                # Arquivos do Gazebo (simulação de robôs)
    ├── mintlify/              # Documentação Mintlify
    ├── system_hw_test/        # Testes de hardware
    ├── cyclonedds/            # Configuração CycloneDDS (comunicação ROS2)
    ├── .venv/                 # Ambiente virtual Python
    ├── pyproject.toml         # Configuração do projeto Python
    ├── Dockerfile             # Configuração Docker
    ├── docker-compose.yml     # Orquestração Docker
    ├── README.md              # Documentação principal do OM1
    └── .git/                  # Repositório Git

/data/                         # Diretórios de dados e imagens dos projetos
├── vitrinezap/
│   └── images/                # Imagens do VitrineZap
│       ├── uploads/           # Imagens enviadas pelos usuários
│       ├── produtos/          # Imagens organizadas por categoria
│       │   ├── perfumaria/    # Imagens de perfumes
│       │   ├── cosmeticos/    # Imagens de cosméticos
│       │   └── outros/        # Outras categorias
│       ├── temp/              # Arquivos temporários
│       ├── thumbnails/        # Miniaturas geradas
│       ├── README.md          # Documentação
│       ├── .gitignore         # Configuração Git
│       └── setup_permissions.sh  # Script de permissões
│
├── motopro/
│   └── images/                # Imagens do MotoPro
│       ├── uploads/
│       ├── produtos/
│       │   ├── perfumaria/
│       │   ├── cosmeticos/
│       │   └── outros/
│       ├── temp/
│       ├── thumbnails/
│       ├── README.md
│       ├── .gitignore
│       └── setup_permissions.sh
│
├── eventix/
│   └── images/                # Imagens do Eventix
│       ├── uploads/
│       ├── produtos/
│       │   ├── perfumaria/
│       │   ├── cosmeticos/
│       │   └── outros/
│       ├── temp/
│       ├── thumbnails/
│       ├── README.md
│       ├── .gitignore
│       └── setup_permissions.sh
│
└── sparkscore/
    └── images/                # Imagens do SparkScore
        ├── uploads/
        ├── produtos/
        │   ├── perfumaria/
        │   ├── cosmeticos/
        │   └── outros/
        ├── temp/
        ├── thumbnails/
        ├── README.md
        ├── .gitignore
        └── setup_permissions.sh
```

**Notas**:
- Cada projeto em `/data/` possui sua própria estrutura de diretórios para armazenamento de imagens, organizadas por categoria e tipo de arquivo. Os diretórios são criados automaticamente e incluem scripts de configuração de permissões.
- `/root/openmind_ws/OM1/` contém o projeto OpenMind OM1, um runtime AI modular para criar agentes de IA multimodais e robôs físicos. Veja mais detalhes no README.md do projeto OM1.

---

## 🏗️ Arquitetura do Sistema

```
┌─────────────────┐
│   Cliente Web   │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│   FastAPI App   │
│  (Porta 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ OpenMind│ │ Logs JSON   │
│  API    │ │ (Loki)      │
└────────┘ └──────┬───────┘
                  │
                  ▼
           ┌─────────────┐
           │  Promtail   │
           └──────┬──────┘
                  │
                  ▼
           ┌─────────────┐
           │    Loki     │
           └──────┬──────┘
                  │
                  ▼
           ┌─────────────┐
           │   Grafana   │
           └─────────────┘
```

### Componentes

1. **OpenMind AI Server** - Aplicação FastAPI principal
2. **systemd Service** - Gerencia o processo da aplicação
3. **Promtail** - Coleta logs do sistema de arquivos
4. **Loki** - Armazena e indexa logs
5. **Grafana** - Visualiza logs e métricas em dashboards

---

## ✅ Pré-requisitos

### No Servidor (Ubuntu)

- Python 3.10 ou superior
- pip e venv
- systemd
- curl (para testes)
- jq (opcional, para visualizar logs JSON)

### No Cliente (Windows/Linux)

- OpenSSH Client
- PowerShell (para Windows)
- Acesso SSH ao servidor

### Contas e Credenciais Necessárias

- **OpenMind.org API Key** - Para análise de imagens
- **API Key da Aplicação** - Para autenticação nas requisições (opcional)

---

## 🚀 Instalação Inicial

### 1. Preparar o Servidor

```bash
# Conectar ao servidor
ssh root@69.169.102.84

# Atualizar sistema
apt update && apt upgrade -y

# Instalar dependências básicas
apt install -y python3 python3-pip python3-venv curl jq

# Criar estrutura de diretórios
mkdir -p /opt/openmind-ai
mkdir -p /var/log/openmind-ai
chmod 755 /var/log/openmind-ai
```

### 2. Criar Ambiente Virtual

```bash
cd /opt/openmind-ai
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

### 3. Copiar Código da Aplicação

```bash
# Do seu computador local (Windows PowerShell)
cd C:\Users\lbule\OneDrive\Documentos\Source\SinapUm

# Copiar arquivos
scp -r app root@69.169.102.84:/opt/openmind-ai/
scp requirements.txt root@69.169.102.84:/opt/openmind-ai/
scp promtail-config.yml root@69.169.102.84:/opt/openmind-ai/
```

### 4. Instalar Dependências

```bash
# No servidor
cd /opt/openmind-ai
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente

```bash
# No servidor, copiar arquivo de exemplo e editar
cd /opt/openmind-ai
cp ENV_EXAMPLE.txt .env
nano .env
```

**IMPORTANTE**: Ajuste os valores no arquivo `.env`, especialmente:
- `OPENMIND_ORG_API_KEY` - Sua chave API do OpenMind.org
- `OPENMIND_AI_API_KEY` - Chave de autenticação (opcional)
- `CORS_ORIGINS` - Origens permitidas (não use `*` em produção)

O arquivo `ENV_EXAMPLE.txt` contém todas as variáveis documentadas e organizadas por seções.

### 6. Criar Serviço systemd

```bash
# Criar arquivo de serviço
nano /etc/systemd/system/openmind-ai.service
```

Conteúdo do serviço:

```ini
[Unit]
Description=OpenMind AI Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/openmind-ai
Environment="PATH=/opt/openmind-ai/venv/bin"
ExecStart=/opt/openmind-ai/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# Logs
StandardOutput=journal
StandardError=journal
SyslogIdentifier=openmind-ai

[Install]
WantedBy=multi-user.target
```

Ativar e iniciar o serviço:

```bash
systemctl daemon-reload
systemctl enable openmind-ai
systemctl start openmind-ai
systemctl status openmind-ai
```

---

## ⚙️ Configuração

### Variáveis de Ambiente

O arquivo `.env` no servidor contém todas as configurações, organizadas em seções:

#### 🔑 API Keys (Obrigatórias)

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `OPENMIND_ORG_API_KEY` | Chave API OpenMind.org (obrigatória) | `om1_live_...` |
| `OPENMIND_ORG_BASE_URL` | URL base da API OpenMind | `https://api.openmind.org/api/core/openai` |
| `OPENMIND_ORG_MODEL` | Modelo de IA a usar | `qwen2.5-vl-72b-instruct` |
| `OPENMIND_AI_API_KEY` | Chave para autenticação (opcional) | `om1_live_...` |

#### 🖼️ Configurações de Imagem

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `MAX_IMAGE_SIZE_MB` | Tamanho máximo da imagem | `10` |
| `ALLOWED_IMAGE_FORMATS` | Formatos permitidos | `jpeg,jpg,png,webp` |
| `IMAGE_MAX_DIMENSION` | Dimensão máxima em pixels | `2048` |

#### ⚙️ Servidor e Performance

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `HOST` | Endereço do servidor | `0.0.0.0` |
| `PORT` | Porta da aplicação | `8000` |
| `RATE_LIMIT_PER_MINUTE` | Limite de requisições/min | `100` |
| `CORS_ORIGINS` | Origens CORS permitidas | `*` |

#### 📊 Logging e Monitoramento

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `LOG_LEVEL` | Nível de log | `INFO` |
| `LOG_FORMAT` | Formato dos logs | `json` |
| `LOG_DIR` | Diretório para logs | `/var/log/openmind-ai` |
| `LOKI_ENABLED` | Habilitar Loki | `True` |
| `LOKI_URL` | URL do Loki | `http://localhost:3100/loki/api/v1/push` |

**📝 Nota**: Veja o arquivo `ENV_EXAMPLE.txt` para todas as variáveis disponíveis com documentação completa.

### Firewall

```bash
# Permitir porta 8000 (se necessário)
ufw allow 8000/tcp
ufw reload
```

---

## 📦 Deploy

### Opção 1: Script Automatizado (PowerShell - Recomendado)

Do seu computador Windows:

```powershell
cd C:\Users\lbule\OneDrive\Documentos\Source\SinapUm
.\DEPLOY_SINAPUM.ps1
```

O script faz automaticamente:
- ✅ Cria backup do código atual
- ✅ Copia arquivos atualizados via SCP
- ✅ Instala dependências
- ✅ Aplica permissões
- ✅ Reinicia o serviço
- ✅ Verifica saúde

**Opções do script:**

```powershell
# Dry-run (simular sem fazer alterações)
.\DEPLOY_SINAPUM.ps1 -DryRun

# Pular backup
.\DEPLOY_SINAPUM.ps1 -SkipBackup

# Personalizar servidor
.\DEPLOY_SINAPUM.ps1 -ServerIP "69.169.102.84" -ServerUser "root"
```

### Opção 2: Deploy Manual

**Passo 1 - Copiar arquivos (do seu computador):**

```powershell
cd C:\Users\lbule\OneDrive\Documentos\Source\SinapUm

# Copiar código
scp -r app root@69.169.102.84:/opt/openmind-ai/
scp requirements.txt root@69.169.102.84:/opt/openmind-ai/
scp promtail-config.yml root@69.169.102.84:/opt/openmind-ai/
```

**Passo 2 - No servidor:**

```bash
ssh root@69.169.102.84

cd /opt/openmind-ai
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Aplicar permissões
chmod -R 755 app/

# Reiniciar serviço
systemctl restart openmind-ai

# Verificar status
systemctl status openmind-ai
```

### Opção 3: Script no Servidor

Se você já copiou os arquivos:

```bash
# No servidor
cd /opt/openmind-ai
chmod +x DEPLOY_RAPIDO.sh
./DEPLOY_RAPIDO.sh
```

---

## 📊 Monitoramento e Logs

### Logs do Sistema (systemd)

```bash
# Ver logs em tempo real
journalctl -u openmind-ai -f

# Ver últimas 100 linhas
journalctl -u openmind-ai -n 100

# Ver logs desde hoje
journalctl -u openmind-ai --since today

# Ver logs de um período específico
journalctl -u openmind-ai --since "2024-01-01 00:00:00" --until "2024-01-01 23:59:59"
```

### Logs Estruturados (JSON)

Os logs estruturados estão em `/var/log/openmind-ai/`:

```bash
# Ver logs gerais
tail -f /var/log/openmind-ai/app.log

# Ver apenas erros
tail -f /var/log/openmind-ai/errors.log

# Ver requisições HTTP
tail -f /var/log/openmind-ai/access.log

# Ver análises de imagens
tail -f /var/log/openmind-ai/analysis.log

# Visualizar JSON formatado (com jq)
tail -f /var/log/openmind-ai/app.log | jq .
```

### Status do Serviço

```bash
# Status do serviço
systemctl status openmind-ai

# Verificar se está rodando
systemctl is-active openmind-ai

# Verificar se está habilitado
systemctl is-enabled openmind-ai
```

### Health Check

```bash
# Verificar saúde da aplicação
curl http://localhost:8000/health

# Verificar versão
curl http://localhost:8000/docs
```

---

## 📈 Integração Grafana/Loki

### Instalação do Loki e Promtail

```bash
# No servidor
# Instalar Loki e Promtail (via Docker ou binários)
# Documentação completa: https://grafana.com/docs/loki/latest/installation/

# Configurar Promtail
cp /opt/openmind-ai/promtail-config.yml /etc/promtail/promtail-config.yml
systemctl restart promtail
```

### Configuração no Grafana


Admin
TroqueEstaSenha123


1. **Adicionar Loki como Data Source:**
   - Acesse Grafana → Configuration → Data Sources
   - Adicione Loki
   - URL: `http://localhost:3100`

2. **Queries Úteis:**

```logql
# Todos os logs da aplicação
{job="openmind-ai"}

# Apenas erros
{job="openmind-ai"} |= "ERROR"

# Requisições HTTP
{job="openmind-ai", logfile="access.log"}

# Análises de imagens
{job="openmind-ai", logfile="analysis.log"}

# Por request_id
{job="openmind-ai"} | json | request_id="abc123"

# Tempo de processamento > 5s
{job="openmind-ai"} | json | processing_time_ms > 5000
```

3. **Dashboard Básico:**

   - Crie um dashboard novo
   - Adicione painéis para:
     - Taxa de requisições por segundo
     - Erros por minuto
     - Tempo médio de processamento
     - Distribuição de status HTTP
     - Últimas requisições

**Ver documentação completa:** `GRAFANA_SETUP.md`

---

## 🛠️ Comandos Úteis

### Gerenciamento do Serviço

```bash
# Iniciar
systemctl start openmind-ai

# Parar
systemctl stop openmind-ai

# Reiniciar
systemctl restart openmind-ai

# Recarregar configuração (sem parar)
systemctl reload openmind-ai  # Se suportado

# Ver status detalhado
systemctl status openmind-ai -l

# Habilitar início automático
systemctl enable openmind-ai

# Desabilitar início automático
systemctl disable openmind-ai
```

### Testes da API

```bash
# Health check
curl http://localhost:8000/health

# Documentação interativa
curl http://localhost:8000/docs
# Ou abra no navegador: http://69.169.102.84:8000/docs

# Teste de análise de imagem
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: multipart/form-data" \
  -F "image=@/caminho/para/imagem.jpg"
```

### Backup e Restauração

```bash
# Criar backup manual
BACKUP_DIR="/opt/openmind-ai/backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/openmind-ai/app "$BACKUP_DIR/"

# Restaurar backup
cp -r /opt/openmind-ai/backups/backup_YYYYMMDD_HHMMSS/app /opt/openmind-ai/
systemctl restart openmind-ai
```

### Limpeza de Logs

```bash
# Limpar logs antigos (manter últimos 30 dias)
find /var/log/openmind-ai -name "*.log" -mtime +30 -delete

# Limpar logs do systemd (manter últimos 7 dias)
journalctl --vacuum-time=7d
```

### Atualização de Dependências

```bash
cd /opt/openmind-ai
source venv/bin/activate

# Atualizar pip
pip install --upgrade pip

# Atualizar todas as dependências
pip install --upgrade -r requirements.txt

# Verificar dependências desatualizadas
pip list --outdated
```

---

## 🐛 Troubleshooting

### Serviço não inicia

```bash
# Ver logs de erro
journalctl -u openmind-ai -n 50 --no-pager

# Verificar se a porta está em uso
netstat -tulpn | grep 8000
# ou
lsof -i :8000

# Verificar permissões
ls -la /opt/openmind-ai/app
ls -la /var/log/openmind-ai

# Testar manualmente
cd /opt/openmind-ai
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Erros de API Key

```bash
# Verificar variáveis de ambiente
cat /opt/openmind-ai/.env | grep API_KEY

# Testar conexão com API
curl -H "Authorization: Bearer $OPENMIND_ORG_API_KEY" \
  https://api.openmind.org/v1/models
```

### Logs não aparecem

```bash
# Verificar se o diretório existe
ls -la /var/log/openmind-ai

# Verificar permissões
chmod 755 /var/log/openmind-ai
chown root:root /var/log/openmind-ai

# Verificar configuração de logging
grep -r "LOG_DIR" /opt/openmind-ai/app/
```

### Aplicação lenta

```bash
# Verificar uso de recursos
htop
# ou
top

# Verificar processos Python
ps aux | grep python

# Verificar espaço em disco
df -h

# Verificar memória
free -h
```

### Erro de conexão externa

```bash
# Verificar firewall
ufw status

# Verificar se o serviço está escutando na interface correta
netstat -tulpn | grep 8000

# Testar localmente
curl http://localhost:8000/health

# Testar externamente (de outro servidor)
curl http://69.169.102.84:8000/health
```

---

## 🔧 Manutenção

### Atualização Regular

Recomenda-se atualizar o código pelo menos uma vez por semana:

```powershell
# Do seu computador
.\DEPLOY_SINAPUM.ps1
```

### Backup Automático

Os scripts de deploy criam backups automaticamente. Para backup manual:

```bash
BACKUP_DIR="/opt/openmind-ai/backups/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /opt/openmind-ai/app "$BACKUP_DIR/"
cp /opt/openmind-ai/.env "$BACKUP_DIR/" 2>/dev/null || true
```

### Monitoramento de Espaço

```bash
# Verificar espaço usado pelos logs
du -sh /var/log/openmind-ai/

# Verificar espaço usado pela aplicação
du -sh /opt/openmind-ai/

# Verificar backups
du -sh /opt/openmind-ai/backups/
```

### Rotação de Logs

Os logs são rotativos automaticamente. Configuração em `app/core/logging_grafana.py`:

- Tamanho máximo por arquivo: 10MB
- Número de backups: 5 arquivos

---

## 📞 Suporte e Contato

### Informações do Projeto

- **Repositório Local**: `C:\Users\lbule\OneDrive\Documentos\Source\SinapUm`
- **Servidor**: `69.169.102.84`
- **Documentação**: Este README.md

### Links Úteis

- [Documentação FastAPI](https://fastapi.tiangolo.com/)
- [Documentação Grafana/Loki](https://grafana.com/docs/loki/latest/)
- [Documentação OpenMind.org API](https://docs.openmind.org/)

### Recursos Adicionais

- `DEPLOY_SINAPUM.ps1` - Script de deploy para Windows
- `DEPLOY_RAPIDO.sh` - Script de deploy para Linux
- `GRAFANA_SETUP.md` - Guia de configuração do Grafana
- `promtail-config.yml` - Configuração do Promtail

---

## 📝 Changelog

### Versão Atual

- ✅ Sistema de logging estruturado (JSON)
- ✅ Integração com Grafana/Loki
- ✅ Middleware de requisições com request_id
- ✅ Logs separados por tipo (app, errors, access, analysis, metrics)
- ✅ Scripts de deploy automatizados
- ✅ Documentação completa

### Próximas Melhorias

- [ ] Métricas Prometheus
- [ ] Dashboard Grafana pré-configurado
- [ ] Alertas automáticos
- [ ] Backup automatizado
- [ ] Testes automatizados

---

**Última atualização**: Janeiro 2024
**Versão**: 1.0.0

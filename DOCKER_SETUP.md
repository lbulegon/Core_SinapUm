# 🐳 Docker Setup - MCP SinapUm

## 📋 Visão Geral

O MCP_SinapUm agora roda completamente em containers Docker, incluindo:
- **Django Application** (porta 5000)
- **PostgreSQL Database** (porta 5432)
- **Volumes persistentes** para dados

## 🚀 Início Rápido

### 1. Preparar arquivo .env

```bash
cd /root/MCP_SinapUm
cp .env.example .env
# Edite .env com suas configurações
nano .env
```

### 2. Parar serviço systemd (se estiver rodando)

```bash
sudo systemctl stop sinapum-django.service
sudo systemctl disable sinapum-django.service
```

### 3. Construir e iniciar containers

```bash
# Construir imagens
docker compose build

# Iniciar containers
docker compose up -d

# Ver logs
docker compose logs -f
```

**Nota:** Use `docker compose` (sem hífen) - é a sintaxe moderna do Docker Compose v2.

### 4. Verificar status

```bash
# Status dos containers
docker compose ps

# Testar aplicação
curl http://localhost:5000/
```

## 📁 Estrutura Docker

```
MCP_SinapUm/
├── Dockerfile              # Imagem do Django
├── docker-compose.yml      # Orquestração dos serviços
├── docker-entrypoint.sh    # Script de inicialização
├── .dockerignore           # Arquivos ignorados no build
├── .env.example           # Exemplo de variáveis de ambiente
└── .env                   # Suas variáveis (não versionado)
```

## 🔧 Serviços

### 1. Web (Django)
- **Container:** `mcp_sinapum_web`
- **Porta:** `5000`
- **Healthcheck:** `http://localhost:5000/`

### 2. Database (PostgreSQL)
- **Container:** `mcp_sinapum_db`
- **Porta:** `5432`
- **Healthcheck:** `pg_isready`

## 📦 Volumes

- `postgres_data`: Dados do PostgreSQL
- `media_data`: Arquivos de mídia do Django
- `static_data`: Arquivos estáticos do Django
- `vitrinezap_images`: Imagens do VitrineZap

## 🔐 Variáveis de Ambiente

Principais variáveis (definidas em `.env`):

- `DEBUG`: Modo debug (True/False)
- `SECRET_KEY`: Chave secreta do Django
- `ALLOWED_HOSTS`: Hosts permitidos (separados por vírgula)
- `POSTGRES_DB`: Nome do banco de dados
- `POSTGRES_USER`: Usuário do PostgreSQL
- `POSTGRES_PASSWORD`: Senha do PostgreSQL
- `DATABASE_URL`: URL completa do banco (opcional)
- `OPENMIND_AI_URL`: URL do OpenMind AI Server
- `OPENMIND_AI_KEY`: Chave do OpenMind AI

## 🛠️ Comandos Úteis

### Gerenciamento de Containers

```bash
# Iniciar
docker compose up -d

# Parar
docker compose down

# Parar e remover volumes (⚠️ apaga dados)
docker compose down -v

# Reiniciar
docker compose restart

# Ver logs
docker compose logs -f web
docker compose logs -f db

# Status
docker compose ps
```

### Django Management

```bash
# Executar comandos Django
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py collectstatic

# Shell Django
docker compose exec web python manage.py shell

# Acessar shell do container
docker compose exec web bash
```

### Banco de Dados

```bash
# Acessar PostgreSQL
docker compose exec db psql -U mcp_user -d mcp_sinapum

# Backup
docker compose exec db pg_dump -U mcp_user mcp_sinapum > backup.sql

# Restore
docker compose exec -T db psql -U mcp_user mcp_sinapum < backup.sql
```

## 🔄 Migração do Systemd para Docker

### Passo 1: Parar serviço systemd

```bash
sudo systemctl stop sinapum-django.service
sudo systemctl disable sinapum-django.service
```

### Passo 2: Migrar dados (se necessário)

Se você tinha dados em outro banco de dados (PostgreSQL ou outro):

```bash
# Exportar dados do banco antigo
cd /root/MCP_SinapUm
python manage.py dumpdata > data_backup.json

# Iniciar containers Docker
docker compose up -d

# Importar dados no PostgreSQL
docker compose exec web python manage.py loaddata data_backup.json
```

### Passo 3: Verificar funcionamento

```bash
# Verificar containers
docker compose ps

# Testar aplicação
curl http://localhost:5000/

# Ver logs
docker compose logs -f
```

## 🐛 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker compose logs web

# Verificar variáveis de ambiente
docker compose exec web env | grep POSTGRES
```

### Erro de conexão com PostgreSQL

```bash
# Verificar se PostgreSQL está saudável
docker compose ps db

# Testar conexão manualmente
docker compose exec web python manage.py dbshell
```

### Problemas com migrações

```bash
# Resetar migrações (⚠️ cuidado)
docker compose exec web python manage.py migrate --fake-initial

# Aplicar migrações manualmente
docker compose exec web python manage.py migrate
```

### Reconstruir containers

```bash
# Reconstruir sem cache
docker compose build --no-cache

# Recriar containers
docker compose up -d --force-recreate
```

## 📊 Monitoramento

### Recursos

```bash
# Uso de recursos
docker stats mcp_sinapum_web mcp_sinapum_db
```

### Logs

```bash
# Logs em tempo real
docker compose logs -f

# Últimas 100 linhas
docker compose logs --tail=100
```

## 🔒 Segurança

1. **Altere as senhas padrão** no `.env`
2. **Use SECRET_KEY forte** em produção
3. **Configure ALLOWED_HOSTS** corretamente
4. **Desabilite DEBUG** em produção
5. **Use volumes nomeados** para dados sensíveis

## 📝 Notas

- O OpenMind AI Server (porta 8000) continua rodando fora do Docker
- Use `host.docker.internal:8000` para acessar serviços do host
- Volumes são persistentes mesmo após `docker compose down`
- Para produção, considere usar Docker Swarm ou Kubernetes

---

**Última atualização:** 2025-12-11


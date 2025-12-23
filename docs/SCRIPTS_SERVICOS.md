# Scripts de Gerenciamento de Serviços

Scripts para gerenciar todos os serviços do sistema de uma vez.

## Scripts Disponíveis

### 1. `restart_all_services.sh` - Reinício Rápido
Reinicia todos os serviços rapidamente (sem remover containers).

```bash
./restart_all_services.sh
```

**Serviços reiniciados:**
- MCP_SinapUm (inclui OpenMind AI, Django, PostgreSQL)
- Evolution API
- SparkScore Service
- DDF Service

### 2. `reset_all_services.sh` - Reset Completo
Reset geral com opções de reset.

```bash
# Reset soft (reinicia apenas)
./reset_all_services.sh soft

# Reset hard (remove e recria containers)
./reset_all_services.sh hard

# Reset rebuild (remove, reconstrói imagens e recria)
./reset_all_services.sh rebuild
```

**Opções:**
- `soft` (padrão): Apenas reinicia os containers
- `hard`: Para, remove e recria os containers
- `rebuild`: Para, remove, reconstrói imagens e recria tudo

## Serviços Gerenciados

1. **MCP_SinapUm** (`/root/MCP_SinapUm/`)
   - Django Web Application
   - PostgreSQL Database
   - OpenMind AI Service (FastAPI)

2. **Evolution API** (`/root/MCP_SinapUm/services/evolution_api/`)
   - WhatsApp Multi-Device REST API
   - PostgreSQL Database
   - Redis

3. **SparkScore Service** (`/root/MCP_SinapUm/services/sparkscore_service/`)
   - Serviço SparkScore

4. **DDF Service** (`/root/MCP_SinapUm/services/ddf_service/`)
   - Serviço DDF
   - PostgreSQL Database
   - Redis

## Comandos Úteis

### Ver status de todos os containers
```bash
docker ps
```

### Ver logs de um serviço específico
```bash
# MCP_SinapUm
cd /root/MCP_SinapUm && docker compose logs -f

# Evolution API
cd /root/MCP_SinapUm/services/evolution_api && docker compose logs -f

# SparkScore
cd /root/MCP_SinapUm/services/sparkscore_service && docker compose logs -f

# DDF
cd /root/MCP_SinapUm/services/ddf_service && docker compose logs -f
```

### Ver logs de um container específico
```bash
docker logs -f <nome_do_container>
```

### Parar todos os serviços
```bash
./reset_all_services.sh hard
# Depois não execute o up, apenas pare
```

### Iniciar todos os serviços
```bash
# MCP_SinapUm
cd /root/MCP_SinapUm && docker compose up -d

# Evolution API
cd /root/MCP_SinapUm/services/evolution_api && docker compose up -d

# SparkScore
cd /root/MCP_SinapUm/services/sparkscore_service && docker compose up -d

# DDF
cd /root/MCP_SinapUm/services/ddf_service && docker compose up -d
```

## Exemplos de Uso

### Reinício rápido após mudanças de código
```bash
./restart_all_services.sh
```

### Reset completo após problemas
```bash
./reset_all_services.sh hard
```

### Rebuild completo após mudanças no Dockerfile
```bash
./reset_all_services.sh rebuild
```

## Notas

- O OpenMind AI Service é gerenciado pelo docker-compose do MCP_SinapUm, não precisa reset separado
- Os scripts aguardam automaticamente os serviços iniciarem antes de mostrar o status
- Em caso de erro em um serviço, os outros continuam sendo processados


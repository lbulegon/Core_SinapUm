# Plano de Migração do OpenMind para MCP_SinapUm/services

## 📋 Objetivo

Mover os serviços OpenMind para `/root/MCP_SinapUm/services/` sem quebrar os serviços.

## 🔍 Análise: Dois Serviços OpenMind Diferentes

### 1. OpenMind AI Server (FastAPI) - `/opt/openmind-ai/`
- **Tipo**: Servidor FastAPI simples
- **Função**: Análise de imagens de produtos (ÉVORA Connect)
- **Porta**: 8000
- **Tecnologia**: FastAPI + Uvicorn
- **Status**: ✅ Provavelmente rodando como serviço systemd ou processo
- **Estrutura**: Aplicação Python com venv

### 2. OpenMind OM1 (Docker) - `/root/openmind_ws/OM1/`
- **Tipo**: OpenMind completo com Docker
- **Função**: Runtime modular de IA para robôs e ambientes digitais
- **Porta**: 8000 (network_mode: host)
- **Tecnologia**: Docker + ROS2 + CycloneDDS
- **Status**: ✅ Container Docker `om1`
- **Estrutura**: Aplicação Docker com volumes

## ⚠️ Conflito de Porta

**AMBOS usam a porta 8000!** Isso significa que:
- Se ambos estiverem rodando, há um conflito
- Precisamos verificar qual está ativo
- Pode ser que apenas um esteja rodando

## ✅ Plano de Migração

### Opção A: Migrar OpenMind AI Server (FastAPI)

**De**: `/opt/openmind-ai/`  
**Para**: `/root/MCP_SinapUm/services/openmind_ai_service/`

#### Passos:

1. **Verificar se está rodando**
   ```bash
   ps aux | grep uvicorn
   systemctl status openmind-ai  # Se tiver serviço systemd
   ```

2. **Parar serviço**
   ```bash
   # Se for systemd
   sudo systemctl stop openmind-ai
   
   # Se for processo manual
   pkill -f "uvicorn.*openmind"
   ```

3. **Copiar estrutura**
   ```bash
   mkdir -p /root/MCP_SinapUm/services/openmind_ai_service
   rsync -av /opt/openmind-ai/ /root/MCP_SinapUm/services/openmind_ai_service/
   ```

4. **Atualizar caminhos em scripts/arquivos de configuração**
   - Verificar `run.sh`, `deploy.sh` se houver
   - Atualizar referências a `/opt/openmind-ai`

5. **Criar docker-compose.yml** (opcional, para padronizar)
   ```yaml
   services:
     openmind_ai:
       build: .
       container_name: openmind_ai
       ports:
         - "8000:8000"
       volumes:
         - ./app:/app/app
         - ./venv:/app/venv
       environment:
         - PORT=8000
   ```

6. **Subir no novo local**
   ```bash
   cd /root/MCP_SinapUm/services/openmind_ai_service
   # Se usar Docker
   docker compose up -d
   
   # Ou se usar venv direto
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

### Opção B: Migrar OpenMind OM1 (Docker)

**De**: `/root/openmind_ws/OM1/`  
**Para**: `/root/MCP_SinapUm/services/openmind_om1_service/`

#### Passos:

1. **Parar container**
   ```bash
   cd /root/openmind_ws/OM1
   docker compose down
   ```

2. **Copiar estrutura**
   ```bash
   mkdir -p /root/MCP_SinapUm/services/openmind_om1_service
   rsync -av --exclude='.git' --exclude='__pycache__' \
     /root/openmind_ws/OM1/ \
     /root/MCP_SinapUm/services/openmind_om1_service/
   ```

3. **Subir no novo local**
   ```bash
   cd /root/MCP_SinapUm/services/openmind_om1_service
   docker compose up -d
   ```

### Opção C: Migrar Ambos (Recomendado)

1. **Decidir qual porta cada um usará**
   - OpenMind AI (FastAPI): 8000 (ou manter)
   - OpenMind OM1: 8001 (ou outro)

2. **Migrar OpenMind AI primeiro** (porta 8000)
3. **Migrar OpenMind OM1 depois** (porta 8001, se mudar)

## 🔍 Verificar Qual Está Rodando

```bash
# Verificar processos
ps aux | grep -E "uvicorn|openmind"

# Verificar containers
docker ps | grep om1

# Verificar porta 8000
sudo lsof -i :8000
netstat -tulpn | grep 8000

# Verificar systemd
systemctl list-units | grep openmind
```

## 📝 Checklist de Migração

### Para OpenMind AI (FastAPI):
- [ ] Identificar como está rodando (systemd, processo manual, Docker)
- [ ] Fazer backup de `/opt/openmind-ai/`
- [ ] Parar serviço atual
- [ ] Copiar para `/root/MCP_SinapUm/services/openmind_ai_service/`
- [ ] Atualizar caminhos em scripts/configurações
- [ ] Criar docker-compose.yml (opcional)
- [ ] Subir no novo local
- [ ] Verificar funcionamento
- [ ] Atualizar referências em outros serviços

### Para OpenMind OM1 (Docker):
- [ ] Parar container atual
- [ ] Fazer backup de `/root/openmind_ws/OM1/`
- [ ] Copiar para `/root/MCP_SinapUm/services/openmind_om1_service/`
- [ ] Atualizar docker-compose.yml (remover version, verificar volumes)
- [ ] Subir no novo local
- [ ] Verificar funcionamento
- [ ] Remover estrutura antiga

## 🆘 Rollback

Se algo der errado:

```bash
# Para OpenMind AI
cd /opt/openmind-ai
# Restaurar serviço original

# Para OpenMind OM1
cd /root/openmind_ws/OM1
docker compose up -d
```

## 📚 Documentação Adicional

- Ver `migrar_openmind.sh` para script automatizado do OM1
- Ver `SUBIR_SERVICOS.md` para instruções de subida

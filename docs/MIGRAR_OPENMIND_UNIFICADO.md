# Migração Unificada do OpenMind - FastAPI

## 🎯 Objetivo

Unificar os serviços OpenMind mantendo **FastAPI como tecnologia padrão** e migrar tudo para `/root/MCP_SinapUm/services/openmind_service/` na **porta 8000**, sem quebrar nenhum serviço.

## 📋 Estratégia

### Serviço Base: OpenMind AI (FastAPI)
- **Origem**: `/opt/openmind-ai/`
- **Tecnologia**: FastAPI + Uvicorn ✅
- **Porta**: 8000 ✅
- **Status**: Funcionando

### Serviço a Migrar: OpenMind OM1 (Docker)
- **Origem**: `/root/openmind_ws/OM1/`
- **Tecnologia**: Docker + ROS2
- **Status**: Verificar se está em uso

**Decisão**: Manter apenas o OpenMind AI (FastAPI) e migrar para a estrutura padronizada.

## ✅ Plano de Migração (Sem Downtime)

### Fase 1: Preparação

1. **Verificar estado atual**
   ```bash
   # Verificar processo FastAPI
   ps aux | grep uvicorn
   
   # Verificar porta 8000
   sudo lsof -i :8000
   
   # Verificar se há serviço systemd
   systemctl list-units | grep openmind
   ```

2. **Fazer backup**
   ```bash
   mkdir -p /root/backup_openmind_$(date +%Y%m%d)
   cp -r /opt/openmind-ai /root/backup_openmind_$(date +%Y%m%d)/
   ```

### Fase 2: Criar Estrutura no Novo Local

1. **Criar diretório**
   ```bash
   mkdir -p /root/MCP_SinapUm/services/openmind_service
   ```

2. **Copiar estrutura completa**
   ```bash
   rsync -av --exclude='venv' --exclude='__pycache__' \
     /opt/openmind-ai/ \
     /root/MCP_SinapUm/services/openmind_service/
   ```

### Fase 3: Dockerizar (Padronizar)

1. **Criar Dockerfile**
   - Baseado em Python 3.11
   - Instalar dependências
   - Copiar aplicação
   - Expor porta 8000

2. **Criar docker-compose.yml**
   - Serviço `openmind_service`
   - Porta 8000:8000
   - Volumes para dados persistentes
   - Variáveis de ambiente

3. **Criar .env** (se necessário)
   - Copiar de ENV_EXAMPLE.txt
   - Ajustar caminhos se necessário

### Fase 4: Migração com Zero Downtime

**Opção A: Migração com Parada Curta (Recomendado)**

```bash
# 1. Parar serviço atual (se for systemd)
sudo systemctl stop openmind-ai  # Se existir

# Ou parar processo manual
pkill -f "uvicorn.*openmind"

# 2. Subir no novo local com Docker
cd /root/MCP_SinapUm/services/openmind_service
docker compose up -d

# 3. Verificar que está funcionando
docker logs openmind_service
curl http://localhost:8000/health

# 4. Se tudo OK, remover serviço antigo (opcional)
# sudo systemctl disable openmind-ai
```

**Opção B: Migração Sem Parada (Avançado)**

1. Subir novo serviço em porta temporária (8001)
2. Testar completamente
3. Parar serviço antigo
4. Mudar novo serviço para porta 8000
5. Verificar funcionamento

### Fase 5: Verificação

1. **Verificar container**
   ```bash
   docker ps | grep openmind_service
   ```

2. **Verificar logs**
   ```bash
   docker logs openmind_service
   ```

3. **Testar endpoints**
   ```bash
   curl http://localhost:8000/
   curl http://localhost:8000/health
   curl http://localhost:8000/docs
   ```

4. **Verificar volumes**
   ```bash
   docker inspect openmind_service | grep -A 10 Mounts
   ```

### Fase 6: Limpeza (Após Confirmação)

1. **Remover estrutura antiga** (apenas após confirmar funcionamento)
   ```bash
   # Fazer backup final antes
   tar -czf /root/backup_openmind_opt_$(date +%Y%m%d).tar.gz /opt/openmind-ai
   
   # Remover (cuidado!)
   # rm -rf /opt/openmind-ai
   ```

2. **Atualizar referências**
   - Verificar outros serviços que referenciam `/opt/openmind-ai`
   - Atualizar para novo caminho ou URL

## 📦 Estrutura Final

```
/root/MCP_SinapUm/services/openmind_service/
├── docker-compose.yml
├── Dockerfile
├── .env
├── requirements.txt
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   └── models/
├── data/              # Dados persistentes (se necessário)
└── README.md
```

## 🔧 Arquivos a Criar

### Dockerfile
- Python 3.11-slim
- Instalar dependências do requirements.txt
- Copiar aplicação
- Expor porta 8000
- Comando: uvicorn app.main:app --host 0.0.0.0 --port 8000

### docker-compose.yml
- Serviço openmind_service
- Porta 8000:8000
- Volumes para dados (se necessário)
- Variáveis de ambiente do .env
- Restart: unless-stopped

## ⚠️ Pontos de Atenção

1. **Variáveis de Ambiente**: Verificar .env e ajustar caminhos se necessário
2. **Volumes de Dados**: Se houver dados persistentes (imagens, etc.), criar volumes
3. **CORS**: Manter configuração de CORS para outros serviços
4. **MEDIA_ROOT**: Verificar onde as imagens são salvas e criar volume se necessário

## 📝 Checklist

- [ ] Backup de `/opt/openmind-ai/`
- [ ] Verificar estado atual do serviço
- [ ] Criar diretório de destino
- [ ] Copiar estrutura completa
- [ ] Criar Dockerfile
- [ ] Criar docker-compose.yml
- [ ] Criar/atualizar .env
- [ ] Parar serviço antigo
- [ ] Subir serviço no novo local
- [ ] Verificar logs e funcionamento
- [ ] Testar todos os endpoints
- [ ] Verificar integração com outros serviços
- [ ] Atualizar documentação
- [ ] Remover estrutura antiga (após confirmação)

## 🆘 Rollback

Se algo der errado:

```bash
# Parar serviço novo
cd /root/MCP_SinapUm/services/openmind_service
docker compose down

# Voltar para o antigo
cd /opt/openmind-ai
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🚀 Script Automatizado

Ver `migrar_openmind_unificado.sh` para execução automatizada de todos os passos.


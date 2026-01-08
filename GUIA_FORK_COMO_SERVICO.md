# Fork do Chatwoot como Serviço no Core_SinapUm
## Como Integrar um Fork ao Docker Compose

**Data**: 2025-01-03

---

## 🎯 RESPOSTA DIRETA

**Fazer fork NÃO muda automaticamente o serviço**. O `docker-compose.yml` usa **imagem Docker**, não o código-fonte diretamente.

Para usar um fork como serviço, você tem **3 opções**:

1. **Buildar imagem Docker própria** (RECOMENDADO se for modificar)
2. **Usar volume mount** (desenvolvimento apenas)
3. **Continuar usando imagem oficial** (se não for modificar código)

---

## 📊 SITUAÇÃO ATUAL

### Configuração Atual (docker-compose.yml)

```yaml
chatwoot_rails:
  image: chatwoot/chatwoot:latest  # ← Usa imagem oficial do Docker Hub
  container_name: mcp_sinapum_chatwoot_rails
  env_file:
    - ./services/chatwoot/.env
  # ... resto da config
```

**Problema**: O código-fonte em `services/chatwoot_service` **NÃO está sendo usado** pelo serviço!

O serviço usa a **imagem pré-compilada** `chatwoot/chatwoot:latest` do Docker Hub.

---

## 🔧 OPÇÕES PARA USAR FORK COMO SERVIÇO

### Opção 1: Buildar Imagem Docker Própria (RECOMENDADO)

#### Como Funciona

1. Fork do código no GitHub
2. Buildar imagem Docker a partir do fork
3. Atualizar docker-compose.yml para usar `build` ao invés de `image`

#### Vantagens

- ✅ Suas modificações são incluídas
- ✅ Imagem otimizada para seu uso
- ✅ Controle total sobre versão
- ✅ Ideal para produção

#### Desvantagens

- ⚠️ Build demora (primeira vez)
- ⚠️ Precisa rebuildar após cada modificação
- ⚠️ Mais complexo

#### Implementação

**Passo 1: Fazer Fork**

```bash
# 1. Fazer fork no GitHub (via interface web)
#    Acesse: https://github.com/chatwoot/chatwoot
#    Clique em "Fork"

# 2. Remover clone atual
cd /root/Core_SinapUm
rm -rf services/chatwoot_service

# 3. Clonar seu fork
git clone https://github.com/SEU_USUARIO/chatwoot.git services/chatwoot_service

# 4. Configurar upstream
cd services/chatwoot_service
git remote add upstream https://github.com/chatwoot/chatwoot.git
```

**Passo 2: Atualizar docker-compose.yml**

```yaml
# ANTES (usa imagem oficial)
chatwoot_rails:
  image: chatwoot/chatwoot:latest

# DEPOIS (builda do código)
chatwoot_rails:
  build:
    context: ./services/chatwoot_service
    dockerfile: docker/Dockerfile
    args:
      - RAILS_ENV=production
  image: core_sinapum_chatwoot:custom  # Nome da imagem customizada
```

**Passo 3: Atualizar chatwoot_sidekiq também**

```yaml
chatwoot_sidekiq:
  build:
    context: ./services/chatwoot_service
    dockerfile: docker/Dockerfile
    args:
      - RAILS_ENV=production
  image: core_sinapum_chatwoot:custom  # Mesma imagem
```

**Passo 4: Buildar e Subir**

```bash
cd /root/Core_SinapUm

# Buildar imagem
docker-compose build chatwoot_rails chatwoot_sidekiq

# Subir serviços
docker-compose up -d chatwoot_rails chatwoot_sidekiq
```

---

### Opção 2: Volume Mount (DESENVOLVIMENTO APENAS)

#### Como Funciona

1. Fork do código no GitHub
2. Montar código local como volume no container
3. Container usa código local (hot-reload)

#### Vantagens

- ✅ Mudanças refletem imediatamente (sem rebuild)
- ✅ Ideal para desenvolvimento/testes
- ✅ Fácil de debugar

#### Desvantagens

- ❌ **NÃO recomendado para produção**
- ❌ Pode ser mais lento
- ❌ Dependências podem ter problemas

#### Implementação

```yaml
chatwoot_rails:
  image: chatwoot/chatwoot:latest  # Ainda usa imagem base
  volumes:
    - ./services/chatwoot_service:/app  # ← Monta código local
    - chatwoot_storage_data:/app/storage
  # ... resto da config
```

**⚠️ ATENÇÃO**: Isso pode não funcionar perfeitamente porque:
- A imagem oficial pode ter configurações específicas
- Dependências podem estar pré-instaladas na imagem
- Pode precisar rodar `bundle install` dentro do container

---

### Opção 3: Continuar com Imagem Oficial (SE NÃO MODIFICAR)

#### Como Funciona

1. Fork apenas para referência/histórico
2. Continua usando `image: chatwoot/chatwoot:latest`
3. Código-fonte não é usado pelo serviço

#### Quando Usar

- ✅ Apenas quer fazer fork para estudo
- ✅ Não vai modificar código agora
- ✅ Quer manter fácil atualização

#### Implementação

**Não precisa mudar nada!** O docker-compose.yml continua como está:

```yaml
chatwoot_rails:
  image: chatwoot/chatwoot:latest  # Continua usando oficial
```

O fork fica apenas como referência no servidor.

---

## 📝 COMPARAÇÃO DAS OPÇÕES

| Aspecto | Build Própria | Volume Mount | Imagem Oficial |
|---------|---------------|--------------|----------------|
| **Modificações incluídas** | ✅ Sim | ✅ Sim | ❌ Não |
| **Tempo de build** | ⚠️ Lento (1ª vez) | ✅ Rápido | ✅ Instantâneo |
| **Hot-reload** | ❌ Não | ✅ Sim | ❌ Não |
| **Produção** | ✅ Ideal | ❌ Não recomendado | ✅ Ideal |
| **Complexidade** | 🟡 Média | 🟡 Média | 🟢 Baixa |
| **Manutenção** | ⚠️ Precisa rebuildar | ⚠️ Pode ter issues | ✅ Fácil |

---

## 🚀 RECOMENDAÇÃO PARA O SEU CASO

### Cenário 1: VAI MODIFICAR código e usar em PRODUÇÃO

→ **Opção 1: Buildar Imagem Própria**

```yaml
# docker-compose.yml
chatwoot_rails:
  build:
    context: ./services/chatwoot_service
    dockerfile: docker/Dockerfile
  image: core_sinapum_chatwoot:custom
```

### Cenário 2: VAI MODIFICAR código apenas para TESTES/DEV

→ **Opção 2: Volume Mount**

```yaml
# docker-compose.yml
chatwoot_rails:
  image: chatwoot/chatwoot:latest
  volumes:
    - ./services/chatwoot_service:/app
```

### Cenário 3: NÃO VAI MODIFICAR (fazer fork só por precaução)

→ **Opção 3: Continuar com Imagem Oficial**

```yaml
# docker-compose.yml (sem mudanças)
chatwoot_rails:
  image: chatwoot/chatwoot:latest
```

---

## 🔄 FLUXO DE TRABALHO COM FORK

### Workflow Completo (Opção 1: Build Própria)

```bash
# 1. Fazer modificações no código
cd /root/Core_SinapUm/services/chatwoot_service
# ... editar arquivos ...

# 2. Commit no fork
git add .
git commit -m "Minha customização"
git push origin master  # Push para seu fork

# 3. Rebuildar imagem
cd /root/Core_SinapUm
docker-compose build chatwoot_rails chatwoot_sidekiq

# 4. Reiniciar serviços
docker-compose up -d chatwoot_rails chatwoot_sidekiq

# 5. (Opcional) Sincronizar com upstream
cd services/chatwoot_service
git fetch upstream
git merge upstream/master  # Ou rebase
```

### Workflow com Volume Mount (Opção 2)

```bash
# 1. Fazer modificações
cd /root/Core_SinapUm/services/chatwoot_service
# ... editar arquivos ...

# 2. (Opcional) Reiniciar container para aplicar
docker-compose restart chatwoot_rails

# 3. Em alguns casos, pode precisar rodar dentro do container:
docker-compose exec chatwoot_rails bundle install
docker-compose exec chatwoot_rails bundle exec rails db:migrate
```

---

## ⚙️ EXEMPLO COMPLETO: Build Própria

### 1. Verificar Dockerfile do Chatwoot

```bash
cd /root/Core_SinapUm/services/chatwoot_service
ls -la docker/Dockerfile
```

### 2. Atualizar docker-compose.yml

```yaml
# /root/Core_SinapUm/docker-compose.yml

services:
  # ... outros serviços ...

  chatwoot_rails:
    build:
      context: ./services/chatwoot_service
      dockerfile: docker/Dockerfile
      args:
        - RAILS_ENV=production
    image: core_sinapum_chatwoot:custom
    container_name: mcp_sinapum_chatwoot_rails
    env_file:
      - ./services/chatwoot_service/.env
    environment:
      - NODE_ENV=production
      - RAILS_ENV=production
      - INSTALLATION_ENV=docker
      - POSTGRES_HOST=chatwoot_postgres
      - POSTGRES_USERNAME=chatwoot
      - POSTGRES_PASSWORD=${CHATWOOT_POSTGRES_PASSWORD:-V$*@eSmnpmYfecMh!j0q%Kccq$6n4LhL}
      - REDIS_URL=redis://:${CHATWOOT_REDIS_PASSWORD:-8gnMzCwQI8LTLzJ2v1moAtCl0tHUZqtB}@chatwoot_redis:6379
    volumes:
      - chatwoot_storage_data:/app/storage
    ports:
      - "3001:3000"
    depends_on:
      chatwoot_postgres:
        condition: service_healthy
      chatwoot_redis:
        condition: service_healthy
    networks:
      - mcp_network
    restart: unless-stopped
    entrypoint: docker/entrypoints/rails.sh
    command: ['bundle', 'exec', 'rails', 's', '-p', '3000', '-b', '0.0.0.0']
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  chatwoot_sidekiq:
    build:
      context: ./services/chatwoot_service
      dockerfile: docker/Dockerfile
      args:
        - RAILS_ENV=production
    image: core_sinapum_chatwoot:custom  # Mesma imagem do rails
    container_name: mcp_sinapum_chatwoot_sidekiq
    env_file:
      - ./services/chatwoot_service/.env
    environment:
      - NODE_ENV=production
      - RAILS_ENV=production
      - INSTALLATION_ENV=docker
      - POSTGRES_HOST=chatwoot_postgres
      - POSTGRES_USERNAME=chatwoot
      - POSTGRES_PASSWORD=${CHATWOOT_POSTGRES_PASSWORD:-V$*@eSmnpmYfecMh!j0q%Kccq$6n4LhL}
      - REDIS_URL=redis://:${CHATWOOT_REDIS_PASSWORD:-8gnMzCwQI8LTLzJ2v1moAtCl0tHUZqtB}@chatwoot_redis:6379
    volumes:
      - chatwoot_storage_data:/app/storage
    depends_on:
      chatwoot_postgres:
        condition: service_healthy
      chatwoot_redis:
        condition: service_healthy
    networks:
      - mcp_network
    restart: unless-stopped
    command: ['bundle', 'exec', 'sidekiq', '-C', 'config/sidekiq.yml']
```

### 3. Buildar e Testar

```bash
cd /root/Core_SinapUm

# Parar serviços atuais (se rodando)
docker-compose stop chatwoot_rails chatwoot_sidekiq

# Buildar (primeira vez demora ~10-15 min)
docker-compose build chatwoot_rails chatwoot_sidekiq

# Subir serviços
docker-compose up -d chatwoot_rails chatwoot_sidekiq

# Verificar logs
docker-compose logs -f chatwoot_rails
```

---

## 🔍 VERIFICAR SE ESTÁ USANDO CÓDIGO LOCAL

```bash
# 1. Ver qual imagem está rodando
docker-compose ps chatwoot_rails

# 2. Ver imagem do container
docker inspect mcp_sinapum_chatwoot_rails | grep Image

# 3. Se usar build própria, deve mostrar:
# "Image": "core_sinapum_chatwoot:custom"
# 
# Se usar imagem oficial, mostra:
# "Image": "chatwoot/chatwoot:latest"
```

---

## ⚠️ IMPORTANTE: .env File

O `.env` continua sendo necessário em `services/chatwoot_service/.env` independente da opção escolhida.

Verifique se o caminho está correto no docker-compose.yml:

```yaml
env_file:
  - ./services/chatwoot_service/.env  # ← Deve existir este arquivo
```

---

## 📚 RESUMO

| Você Vai... | Use... | Ação no docker-compose.yml |
|-------------|--------|----------------------------|
| **Modificar código em produção** | Fork + Build própria | Trocar `image:` por `build:` |
| **Modificar código em dev/testes** | Fork + Volume mount | Adicionar `volumes: - ./services/chatwoot_service:/app` |
| **Não modificar (apenas referência)** | Fork (opcional) | **Nada** (continua `image:`) |
| **Não modificar (sem fork)** | Clone/Submodule | **Nada** (continua `image:`) |

---

**Última atualização**: 2025-01-03


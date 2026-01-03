# Chatwoot - Instalação e Configuração

## 📋 Serviços Configurados

O Chatwoot foi adicionado ao `docker-compose.yml` com os seguintes serviços:

1. **chatwoot_postgres** - Banco de dados PostgreSQL (porta 5435)
2. **chatwoot_redis** - Cache Redis (porta 6381)
3. **chatwoot_rails** - Aplicação principal (porta 3001)
4. **chatwoot_sidekiq** - Worker para processamento de jobs em background

## 🚀 Como Iniciar

### Iniciar todos os serviços do Chatwoot:

```bash
cd /root/Core_SinapUm
docker-compose up -d chatwoot_postgres chatwoot_redis chatwoot_rails chatwoot_sidekiq
```

### Ou iniciar todos os serviços (incluindo Chatwoot):

```bash
cd /root/Core_SinapUm
docker-compose up -d
```

## 🔍 Verificar Status

```bash
# Ver status dos containers do Chatwoot
docker-compose ps | grep chatwoot

# Ver logs do Chatwoot Rails
docker-compose logs -f chatwoot_rails

# Ver logs do Sidekiq
docker-compose logs -f chatwoot_sidekiq
```

## 🔧 Configuração

### Variáveis de Ambiente

O Chatwoot usa o arquivo `.env` em `/root/Core_SinapUm/services/chatwoot/.env`

**Variáveis importantes:**
- `FRONTEND_URL` - URL onde o Chatwoot estará acessível (ex: https://chat.sinapum.com)
- `POSTGRES_HOST` - Nome do serviço PostgreSQL (chatwoot_postgres)
- `POSTGRES_USERNAME` - Usuário do banco (chatwoot)
- `POSTGRES_PASSWORD` - Senha do banco
- `REDIS_URL` - URL completa do Redis com senha
- `SECRET_KEY_BASE` - Chave secreta para Rails (já configurada)

### Portas

- **3001** - Aplicação Rails (mapeada da porta interna 3000)
- **5435** - PostgreSQL (mapeada da porta interna 5432)
- **6381** - Redis (mapeada da porta interna 6379)

## 📝 Primeira Instalação

Após iniciar os serviços pela primeira vez, você precisa executar as migrações:

```bash
# Executar migrações do banco de dados
docker-compose exec chatwoot_rails bundle exec rails db:chatwoot_prepare

# Ou se preferir executar manualmente:
docker-compose exec chatwoot_rails bundle exec rails db:create
docker-compose exec chatwoot_rails bundle exec rails db:migrate
docker-compose exec chatwoot_rails bundle exec rails db:seed
```

## 👤 Criar Primeiro Usuário Admin

```bash
docker-compose exec chatwoot_rails bundle exec rails runner "user = Account.find_by(name: 'master').users.create!(name: 'Admin', email: 'admin@example.com', password: 'password123', role: :administrator)"
```

**Ou via interface:**
1. Acesse http://seu-ip:3001 ou https://chat.sinapum.com
2. Siga o processo de criação de conta (se `ENABLE_ACCOUNT_SIGNUP=true`)
3. Ou use a API para criar conta

## 🔄 Comandos Úteis

### Reiniciar serviços:

```bash
docker-compose restart chatwoot_rails chatwoot_sidekiq
```

### Parar serviços:

```bash
docker-compose stop chatwoot_rails chatwoot_sidekiq chatwoot_postgres chatwoot_redis
```

### Ver logs em tempo real:

```bash
docker-compose logs -f chatwoot_rails
docker-compose logs -f chatwoot_sidekiq
```

### Acessar console Rails:

```bash
docker-compose exec chatwoot_rails bundle exec rails console
```

## 🌐 Acesso

- **Interface Web**: http://seu-ip:3001 ou https://chat.sinapum.com
- **API**: http://seu-ip:3001/api/v1

## 📚 Documentação

- Documentação oficial: https://www.chatwoot.com/docs
- Variáveis de ambiente: https://www.chatwoot.com/docs/self-hosted/configuration/environment-variables

## ⚠️ Notas

- A porta 3000 já está em uso pelo Grafana, por isso o Chatwoot usa a porta 3001
- Certifique-se de configurar o `FRONTEND_URL` corretamente no `.env`
- O Chatwoot precisa de SSL para produção (configure `FORCE_SSL=true` e use um proxy reverso)


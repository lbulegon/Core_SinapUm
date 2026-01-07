# Configuração de Variáveis de Ambiente WhatsApp

## ✅ Variáveis Adicionadas

As seguintes variáveis de ambiente foram adicionadas ao `docker-compose.yml` no serviço `web`:

### WhatsApp Gateway - Provider Selection
- `WHATSAPP_PROVIDER` (default: `legacy`)
- `WHATSAPP_GATEWAY_PROVIDER` (default: `legacy`)

### WhatsApp Gateway - Configurações de Envio
- `WHATSAPP_SEND_ENABLED` (default: `False`)
- `WHATSAPP_SHADOW_MODE` (default: `True`)
- `WHATSAPP_ENABLED_SHOPPERS` (default: vazio)

### WhatsApp Canonical Events v1.0
- `WHATSAPP_CANONICAL_EVENTS_ENABLED` (default: `True`)
- `WHATSAPP_CANONICAL_SHADOW_MODE` (default: `True`)

### WhatsApp Routing
- `WHATSAPP_ROUTING_ENABLED` (default: `False`)
- `WHATSAPP_GROUP_ROUTING_ENABLED` (default: `False`)
- `WHATSAPP_ASSIGNMENT_POLICY` (default: `default`)

### WhatsApp Simulator
- `WHATSAPP_SIM_ENABLED` (default: `True`)

## 📝 Valores Padrão (Modo Seguro para Dev)

Os valores padrão configurados são seguros para desenvolvimento:

- ✅ **Shadow Mode ativo** - não envia mensagens reais
- ✅ **Envio desabilitado** - modo seguro
- ✅ **Eventos canônicos habilitados** - com shadow mode
- ✅ **Simulador habilitado** - para testes

## 🔄 Como Aplicar

### Opção 1: Recriar Container

```bash
cd /root/Core_SinapUm
docker compose up -d --force-recreate web
```

### Opção 2: Reiniciar Container

```bash
docker compose restart web
```

### Opção 3: Usar Variáveis de Ambiente Externas

Você pode definir as variáveis em um arquivo `.env` ou exportá-las antes de subir o container:

```bash
export WHATSAPP_SEND_ENABLED=False
export WHATSAPP_SHADOW_MODE=True
docker compose up -d
```

## 🧪 Verificar Configuração

Após aplicar as mudanças, execute o comando de diagnóstico:

```bash
docker exec mcp_sinapum_web python manage.py whatsapp_diagnose --skip-checks
```

As variáveis devem aparecer como **✓ definidas** em vez de **⚠ Não definido**.

## 📚 Arquivo de Exemplo

Um arquivo de exemplo completo está disponível em:
- `/root/Core_SinapUm/WHATSAPP_ENV_EXAMPLE.txt`

Este arquivo contém:
- Descrição de cada variável
- Valores recomendados por ambiente (dev/produção)
- Notas e recomendações

## ⚙️ Configurações por Ambiente

### Desenvolvimento (Recomendado)

```bash
WHATSAPP_PROVIDER=simulated
WHATSAPP_GATEWAY_PROVIDER=simulated
WHATSAPP_SEND_ENABLED=False
WHATSAPP_SHADOW_MODE=True
WHATSAPP_CANONICAL_EVENTS_ENABLED=True
WHATSAPP_CANONICAL_SHADOW_MODE=True
WHATSAPP_ROUTING_ENABLED=False
WHATSAPP_SIM_ENABLED=True
```

### Produção

```bash
WHATSAPP_PROVIDER=legacy
WHATSAPP_GATEWAY_PROVIDER=legacy
WHATSAPP_SEND_ENABLED=True
WHATSAPP_SHADOW_MODE=False
WHATSAPP_CANONICAL_EVENTS_ENABLED=True
WHATSAPP_CANONICAL_SHADOW_MODE=False
WHATSAPP_ROUTING_ENABLED=True
WHATSAPP_SIM_ENABLED=False
```

## 🔍 Localização no docker-compose.yml

As variáveis foram adicionadas na seção `environment` do serviço `web` (linhas ~92-108):

```yaml
web:
  environment:
    # ... outras variáveis ...
    # WhatsApp Gateway - Provider Selection
    - WHATSAPP_PROVIDER=${WHATSAPP_PROVIDER:-legacy}
    - WHATSAPP_GATEWAY_PROVIDER=${WHATSAPP_GATEWAY_PROVIDER:-legacy}
    # ... etc ...
```

## ✅ Status

- ✅ Variáveis adicionadas ao `docker-compose.yml`
- ✅ Valores padrão configurados (modo seguro)
- ✅ Arquivo de exemplo criado (`WHATSAPP_ENV_EXAMPLE.txt`)
- ⏳ Aguardando recriação do container para aplicar

## 📝 Notas

- Todas as variáveis são opcionais (têm valores padrão)
- Valores padrão são seguros para desenvolvimento
- Para produção, ajuste `WHATSAPP_SEND_ENABLED=True` e `WHATSAPP_SHADOW_MODE=False`
- Use `WHATSAPP_ENABLED_SHOPPERS` para habilitar apenas shoppers específicos

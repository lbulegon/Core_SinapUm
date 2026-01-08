# Quick Start - Nova Arquitetura WhatsApp

## 🚀 Início Rápido

### 1. Ativar Feature Flags

#### Core_SinapUm
```bash
# No .env ou variáveis de ambiente
export FEATURE_EVOLUTION_MULTI_TENANT=true
export FEATURE_OPENMIND_ENABLED=true
```

#### Évora/VitrineZap
```bash
# No .env ou variáveis de ambiente
export FEATURE_CONSOLE_ENABLED=true
export CORE_API_BASE_URL=http://69.169.102.84:5000
export CORE_API_TOKEN=seu-token-aqui
```

### 2. Rodar Migrations

```bash
cd /root/Core_SinapUm
python manage.py migrate app_whatsapp_gateway
python manage.py migrate app_conversations
```

### 3. Testar

```bash
# Testar webhook
python scripts/smoke_test_evolution_webhook.py

# Testar sugestão
python scripts/smoke_test_suggestion_send.py
```

### 4. Acessar Console

1. Acesse: `http://69.169.102.84:8000/console/` (Évora)
2. Faça login como Personal Shopper
3. Clique em "Conectar WhatsApp"
4. Escaneie o QR Code
5. Comece a receber mensagens!

---

## 📝 Endpoints Principais

### Core_SinapUm
- `POST /webhooks/evolution/<instance_id>/messages` - Receber webhooks
- `POST /instances/evolution/create` - Criar instância
- `GET /instances/evolution/<instance_id>/qr` - Obter QR Code
- `GET /console/conversations?shopper_id=...` - Listar conversas
- `POST /console/suggestions/<id>/send` - Enviar sugestão

### Évora/VitrineZap
- `GET /console/` - Dashboard
- `GET /console/conversations/` - Lista de conversas
- `GET /console/conversations/<id>/` - Detalhe de conversa
- `GET /console/connect/` - Conectar WhatsApp

---

## 🔍 Verificar Arquitetura

```bash
# Verificar um arquivo
python scripts/check_architecture.py --file app_whatsapp_gateway/views.py

# Verificar todos os arquivos
python scripts/check_architecture.py --all
```

---

**Pronto para usar!** 🎉


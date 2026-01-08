# Feature Flags Habilitadas - Nova Arquitetura

## ✅ Status

As feature flags foram **habilitadas** nos arquivos `.env`:

### Core_SinapUm (`/root/Core_SinapUm/.env`)

```bash
# Feature Flags
FEATURE_EVOLUTION_MULTI_TENANT=true
FEATURE_OPENMIND_ENABLED=true

# Evolution API
EVOLUTION_BASE_URL=http://69.169.102.84:8004
EVOLUTION_API_KEY=GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg
EVOLUTION_TIMEOUT=30

# OpenMind AI
OPENMIND_BASE_URL=http://69.169.102.84:8001
OPENMIND_TOKEN=om1_live_7d4102a1bf72cc497d7651beb6a98292764b1f77df947c82d086506038ea6b9921efb9d9833045d1

# VitrineZap API (MCP Tools)
VITRINEZAP_BASE_URL=http://69.169.102.84:8000
INTERNAL_API_TOKEN=e6994b05d473440f6c677604ef39188867c4564c54908ea47fdb0f30005945e2
```

### Évora/VitrineZap (`/root/Source/evora/.env`)

```bash
# Feature Flags
FEATURE_CONSOLE_ENABLED=true

# Core API
CORE_API_BASE_URL=http://69.169.102.84:5000
CORE_API_TOKEN=e6994b05d473440f6c677604ef39188867c4564c54908ea47fdb0f30005945e2
```

---

## 🚀 Próximos Passos

1. **Reiniciar serviços** para carregar as novas variáveis:
   ```bash
   # Core_SinapUm
   cd /root/Core_SinapUm
   # Reiniciar serviço Django
   
   # Évora/VitrineZap
   cd /root/Source/evora
   # Reiniciar serviço Django
   ```

2. **Rodar migrations**:
   ```bash
   cd /root/Core_SinapUm
   python manage.py migrate app_whatsapp_gateway
   python manage.py migrate app_conversations
   ```

3. **Testar**:
   ```bash
   python scripts/smoke_test_evolution_webhook.py
   ```

4. **Acessar console**:
   - URL: `http://69.169.102.84:8000/console/`
   - Login como Personal Shopper
   - Conectar WhatsApp

---

## ⚠️ Importante

- As feature flags estão **habilitadas** - a nova arquitetura está **ativa**
- O código antigo continua funcionando (não foi removido)
- URLs novas estão disponíveis:
  - `/webhooks/evolution/*` (Core)
  - `/console/*` (Évora)
  - `/ai/*` (Core)
  - `/mcp/*` (Core)

---

**Data:** 2026-01-03  
**Status:** ✅ Feature flags habilitadas


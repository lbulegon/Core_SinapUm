# Guia de Migração Gradual - WhatsApp Gateway

## 🎯 Objetivo

Migrar gradualmente para usar o WhatsApp Gateway padronizado sem quebrar código existente.

## 📋 Fases de Migração

### Fase 0: Gateway usando Legacy Wrapper (Default) ✅ PRONTO

**Status:** Implementado e funcionando

**Configuração:**
```bash
WHATSAPP_PROVIDER=legacy
WHATSAPP_SEND_ENABLED=true
```

**O que acontece:**
- Gateway encapsula integrações existentes
- Código legado continua funcionando normalmente
- Novos serviços podem usar gateway
- Zero impacto no código existente

**Como testar:**
```python
from core.services.whatsapp.gateway import get_whatsapp_gateway

gateway = get_whatsapp_gateway()
result = gateway.send_text(
    to="5511999999999",
    text="Teste",
    metadata={'shopper_id': 'test'}
)
```

**Checklist:**
- [x] Gateway implementado
- [x] Legacy wrapper funcionando
- [x] Feature flags configuradas
- [ ] Testar em ambiente de desenvolvimento
- [ ] Documentar para equipe

---

### Fase 1: Testes com Simulated em Dev

**Objetivo:** Testar gateway sem WhatsApp real

**Configuração Dev:**
```bash
WHATSAPP_PROVIDER=simulated
WHATSAPP_SEND_ENABLED=true
```

**Configuração Produção:**
```bash
WHATSAPP_PROVIDER=legacy
WHATSAPP_SEND_ENABLED=true
```

**O que acontece:**
- Dev: Mensagens são gravadas em `core_whatsapp_simulated_message`
- Produção: Continua usando legacy (sem mudança)

**Migration necessária:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Como testar:**
```python
# Em dev, usar simulated
gateway = get_whatsapp_gateway()
result = gateway.send_text(to="5511999999999", text="Teste")

# Verificar mensagem gravada
from core.services.whatsapp.providers.provider_simulated import SimulatedMessage
messages = SimulatedMessage.objects.filter(to="+5511999999999")
```

**Checklist:**
- [ ] Aplicar migration do SimulatedMessage
- [ ] Configurar WHATSAPP_PROVIDER=simulated em dev
- [ ] Testar envio de mensagens
- [ ] Verificar mensagens gravadas no banco
- [ ] Validar que produção não é afetada

---

### Fase 2: Habilitar Provider Real Novo por Feature Flag

**Objetivo:** Migrar gradualmente para provider novo (ex: Evolution direto)

**Configuração (Shoppers Específicos):**
```bash
WHATSAPP_PROVIDER=evolution
WHATSAPP_ENABLED_SHOPPERS=shopper_id_1,shopper_id_2
```

**O que acontece:**
- Apenas shoppers na lista usam provider novo
- Outros shoppers continuam usando legacy
- Pode testar com poucos shoppers primeiro

**Como implementar Provider Evolution direto:**

1. Criar `provider_evolution.py`:

```python
from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth
from app_whatsapp_gateway.clients.evolution_client import EvolutionClient

class ProviderEvolution(IWhatsAppProvider):
    @property
    def name(self) -> str:
        return "evolution"
    
    def __init__(self):
        self.client = EvolutionClient()
        self.instance_key = getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'default')
    
    def send_text(self, to: str, text: str, metadata: Optional[Dict] = None) -> ProviderResult:
        result = self.client.send_text(
            instance_id=self.instance_key,
            to=to,
            text=text
        )
        # Converter para ProviderResult
        ...
```

2. Registrar no gateway:

```python
elif provider_name == 'evolution':
    from .providers.provider_evolution import ProviderEvolution
    self._provider = ProviderEvolution()
```

3. Habilitar por shopper:

```bash
WHATSAPP_PROVIDER=evolution
WHATSAPP_ENABLED_SHOPPERS=shopper_id_1
```

**Checklist:**
- [ ] Implementar provider novo (Evolution, Cloud, etc.)
- [ ] Registrar no gateway
- [ ] Testar com 1 shopper
- [ ] Monitorar logs e erros
- [ ] Expandir para mais shoppers gradualmente
- [ ] Remover WHATSAPP_ENABLED_SHOPPERS quando todos migrados

---

### Fase 3: Migração Completa (Opcional)

**Objetivo:** Todos usam provider novo

**Configuração:**
```bash
WHATSAPP_PROVIDER=evolution
WHATSAPP_ENABLED_SHOPPERS=  # vazio = todos
```

**O que acontece:**
- Todos os shoppers usam provider novo
- Legacy wrapper pode ser mantido como fallback

**Checklist:**
- [ ] Validar que todos os shoppers funcionam
- [ ] Monitorar métricas e erros
- [ ] Documentar mudança
- [ ] Considerar remover legacy wrapper (futuro)

---

## 🔄 Rollback

Se algo der errado, sempre pode voltar:

```bash
# Voltar para legacy
WHATSAPP_PROVIDER=legacy
WHATSAPP_ENABLED_SHOPPERS=  # vazio = todos
```

Ou desabilitar completamente:

```bash
WHATSAPP_SEND_ENABLED=false
```

## 📊 Monitoramento

### Logs Estruturados

O gateway sempre loga com metadata:

```python
logger.info(
    "[WhatsAppGateway] Enviando mensagem via legacy",
    extra={
        'provider': 'legacy',
        'to': '5511999999999',
        'shopper_id': 'uuid',
        'skm_id': 'skm-123',
    }
)
```

### Métricas Recomendadas

- Taxa de sucesso por provider
- Tempo de resposta por provider
- Erros por tipo
- Uso por shopper_id

## ⚠️ Regras de Ouro

1. **Nunca alterar código legado** - Apenas encapsular
2. **Sempre ter fallback** - Se provider novo falhar, usar legacy
3. **Feature flags sempre** - Pode desabilitar a qualquer momento
4. **Logging completo** - Sempre logar sucesso e erro
5. **Testar em dev primeiro** - Usar simulated ou noop

## ✅ Checklist Final

- [x] Gateway implementado
- [x] Legacy wrapper funcionando
- [x] Providers noop e simulated implementados
- [x] Feature flags configuradas
- [x] Documentação completa
- [ ] Testes em dev
- [ ] Migração gradual por shopper
- [ ] Monitoramento configurado

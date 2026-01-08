# WhatsApp Gateway - Camada de Abstração Padrão

Camada de abstração para envio de mensagens WhatsApp que permite trocar providers sem alterar código.

## 📋 Características

- ✅ **100% Aditivo**: Não altera código existente
- ✅ **Feature Flags**: Controlado por variáveis de ambiente
- ✅ **Modo Shadow**: Duplica logs sem enviar (para testes)
- ✅ **Providers Plugáveis**: Legacy, Simulated, NoOp, Evolution, Cloud, Baileys
- ✅ **Logging Estruturado**: Com shopper_id, skm_id, correlation_id
- ✅ **Nunca Quebra**: Retorna erro padronizado se provider falhar

## 🚀 Uso Básico

```python
from core.services.whatsapp.gateway import get_whatsapp_gateway

gateway = get_whatsapp_gateway()

# Enviar texto
result = gateway.send_text(
    to="5511999999999",
    text="Olá! Esta é uma mensagem de teste.",
    metadata={
        'shopper_id': 'uuid-do-shopper',
        'skm_id': 'skm-123',
        'correlation_id': 'corr-456'
    }
)

if result.is_success():
    print(f"Mensagem enviada: {result.message_id}")
else:
    print(f"Erro: {result.error}")

# Enviar mídia
result = gateway.send_media(
    to="5511999999999",
    media_url="https://example.com/image.jpg",
    caption="Legenda da imagem",
    metadata={'shopper_id': 'uuid'}
)
```

## ⚙️ Configuração

### Variáveis de Ambiente

```bash
# Provider ativo (legacy, simulated, noop, evolution, cloud, baileys)
WHATSAPP_PROVIDER=legacy

# Habilitar/desabilitar envio
WHATSAPP_SEND_ENABLED=true

# Modo shadow (logar sem enviar)
WHATSAPP_SHADOW_MODE=false

# Shoppers habilitados (opcional, separado por vírgula)
WHATSAPP_ENABLED_SHOPPERS=shopper_id_1,shopper_id_2
```

### Settings.py

```python
# Configurações opcionais
WHATSAPP_PROVIDER = 'legacy'  # default
WHATSAPP_SEND_ENABLED = True
WHATSAPP_SHADOW_MODE = False
WHATSAPP_ENABLED_SHOPPERS = []  # vazio = todos habilitados
```

## 🔌 Providers Disponíveis

### 1. Legacy (Padrão)

Encapsula integrações existentes:
- `app_whatsapp_gateway.EvolutionClient` (Core - multi-tenant)
- `app_whatsapp.WhatsAppRouter` (Core - gateway plugável)
- `EvolutionAPIService` (Évora - se disponível)

**Uso:**
```bash
WHATSAPP_PROVIDER=legacy
```

### 2. Simulated

Simula envio e grava em tabela local (`core_whatsapp_simulated_message`).

**Uso:**
```bash
WHATSAPP_PROVIDER=simulated
```

**Migration necessária:**
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. NoOp

Não envia nada, apenas loga. Útil para desenvolvimento.

**Uso:**
```bash
WHATSAPP_PROVIDER=noop
```

### 4. Evolution, Cloud, Baileys

Por enquanto redirecionam para `legacy`. Implementação futura.

## 📊 Resultado Padronizado

Todos os métodos retornam `ProviderResult`:

```python
@dataclass
class ProviderResult:
    provider_name: str
    status: str  # "queued", "sent", "failed"
    message_id: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def is_success(self) -> bool:
        return self.status in ("queued", "sent")
    
    def is_failed(self) -> bool:
        return self.status == "failed"
```

## 🔧 Adicionar Novo Provider

1. Criar provider em `core/services/whatsapp/providers/`:

```python
from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth

class ProviderCustom(IWhatsAppProvider):
    @property
    def name(self) -> str:
        return "custom"
    
    def send_text(self, to: str, text: str, metadata: Optional[Dict] = None) -> ProviderResult:
        # Implementar envio
        return ProviderResult(
            provider_name=self.name,
            status="sent",
            message_id="msg_123"
        )
    
    def send_media(self, to: str, media_url: str, caption: Optional[str] = None, metadata: Optional[Dict] = None) -> ProviderResult:
        # Implementar envio de mídia
        pass
    
    def healthcheck(self) -> ProviderHealth:
        # Implementar healthcheck
        pass
```

2. Registrar no gateway (`gateway.py`):

```python
elif provider_name == 'custom':
    from .providers.provider_custom import ProviderCustom
    self._provider = ProviderCustom()
```

3. Configurar via env var:

```bash
WHATSAPP_PROVIDER=custom
```

## 🧪 Testar sem WhatsApp Real

### Opção 1: NoOp (Apenas Loga)

```bash
WHATSAPP_PROVIDER=noop
WHATSAPP_SEND_ENABLED=true
```

### Opção 2: Simulated (Grava Localmente)

```bash
WHATSAPP_PROVIDER=simulated
WHATSAPP_SEND_ENABLED=true
```

### Opção 3: Shadow Mode (Loga sem Enviar)

```bash
WHATSAPP_PROVIDER=legacy  # ou qualquer provider
WHATSAPP_SHADOW_MODE=true
```

## 📝 Logging Estruturado

O gateway loga automaticamente com metadata:

```python
logger.info(
    "[WhatsAppGateway] Enviando mensagem via legacy",
    extra={
        'provider': 'legacy',
        'to': '5511999999999',
        'text_length': 50,
        'shopper_id': 'uuid',
        'skm_id': 'skm-123',
        'correlation_id': 'corr-456',
    }
)
```

## 🔄 Migração Gradual

### Fase 0: Gateway usando Legacy (Default)

```bash
WHATSAPP_PROVIDER=legacy
WHATSAPP_SEND_ENABLED=true
```

- Gateway encapsula integrações existentes
- Código legado continua funcionando
- Novos serviços usam gateway

### Fase 1: Testes com Simulated em Dev

```bash
# Dev
WHATSAPP_PROVIDER=simulated
WHATSAPP_SEND_ENABLED=true

# Produção
WHATSAPP_PROVIDER=legacy
WHATSAPP_SEND_ENABLED=true
```

### Fase 2: Habilitar Provider Real Novo por Feature Flag

```bash
# Shoppers específicos
WHATSAPP_PROVIDER=evolution
WHATSAPP_ENABLED_SHOPPERS=shopper_id_1,shopper_id_2

# Todos (quando estiver pronto)
WHATSAPP_PROVIDER=evolution
WHATSAPP_ENABLED_SHOPPERS=  # vazio = todos
```

## ⚠️ Garantias

- ✅ **Não Quebra**: Se provider falhar, retorna erro padronizado
- ✅ **Logging**: Sempre loga (sucesso ou erro)
- ✅ **Feature Flags**: Pode ser desabilitado completamente
- ✅ **Shadow Mode**: Pode logar sem enviar
- ✅ **Retrocompatibilidade**: Legacy wrapper mantém compatibilidade

## 📚 Exemplo de Uso

Ver `Source/evora/app_delivery_area/delivery_notifier.py` para exemplo completo de integração.

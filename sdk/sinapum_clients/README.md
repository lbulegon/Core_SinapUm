# SinapUm Clients SDK

Biblioteca de clientes HTTP para serviços do Core_SinapUm.  
Uso em orbitais (Evora, MrFoo) para desacoplar de imports internos do Core.

## Instalação

```bash
# No Evora ou outro orbital
pip install -e /path/to/Core_SinapUm/sdk/sinapum_clients
# ou adicione ao requirements.txt como dependência local
```

## Uso

```python
from sinapum_clients import (
    CreativeEngineClient,
    SparkScoreClient,
    ShopperBotClient,
    OpenMindClient,
    WhatsAppGatewayClient,
)

# Creative Engine
ce = CreativeEngineClient(
    base_url="http://core:5000",
    api_token="...",
)
result = ce.generate_text("Gere um post para Instagram", context={"tone": "elegante"})

# SparkScore
ss = SparkScoreClient(base_url="http://sparkscore:8006", api_key="...")
score = ss.score_content("Texto do post")

# WhatsApp Gateway (substitui core.services.whatsapp.gateway)
wa = WhatsAppGatewayClient(
    base_url="http://whatsapp_gateway:8007",
    api_key="...",
    instance_id="user_123",
)
wa.send_text(to="5511999999999", text="Olá!")
```

## Configuração via Django

```python
# settings.py do Evora
from decouple import config

CORE_SINAPUM_BASE_URL = config("CORE_SINAPUM_BASE_URL", default="")
WHATSAPP_BAILEYS_GATEWAY_URL = config("WHATSAPP_BAILEYS_GATEWAY_URL", default="")
WHATSAPP_BAILEYS_GATEWAY_API_KEY = config("WHATSAPP_BAILEYS_GATEWAY_API_KEY", default="")
SPARKSCORE_URL = config("SPARKSCORE_URL", default="")
SHOPPERBOT_BASE_URL = config("SHOPPERBOT_BASE_URL", default="")
OPENMIND_AI_URL = config("OPENMIND_AI_URL", default="")
```

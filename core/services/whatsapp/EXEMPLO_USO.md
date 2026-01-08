# Exemplo de Uso - WhatsApp Gateway

## Exemplo 1: DeliveryNotifier (Évora)

O `DeliveryNotifier` em `Source/evora/app_delivery_area/delivery_notifier.py` foi atualizado para usar o gateway:

```python
from core.services.whatsapp.gateway import get_whatsapp_gateway

def _send_whatsapp_message(self, phone: str, message: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    # Tentar usar gateway padronizado primeiro
    try:
        from core.services.whatsapp.gateway import get_whatsapp_gateway
        
        gateway = get_whatsapp_gateway()
        result = gateway.send_text(
            to=phone,
            text=message,
            metadata=metadata or {}
        )
        
        if result.is_success():
            return {
                'success': True,
                'message_id': result.message_id,
                'provider': result.provider_name
            }
        else:
            return {
                'success': False,
                'error': result.error,
                'provider': result.provider_name
            }
    except ImportError:
        # Fallback para serviços existentes
        return self._send_whatsapp_message_legacy(phone, message)
```

## Exemplo 2: Novo Service (Core_SinapUm)

Criar novo service que usa gateway:

```python
# app_exemplo/services/notification_service.py
from core.services.whatsapp.gateway import get_whatsapp_gateway

class NotificationService:
    """Service de notificações usando WhatsApp Gateway"""
    
    def send_order_confirmation(self, order, customer):
        """Envia confirmação de pedido"""
        gateway = get_whatsapp_gateway()
        
        message = f"✅ Pedido {order.number} confirmado!"
        
        result = gateway.send_text(
            to=customer.phone,
            text=message,
            metadata={
                'shopper_id': str(order.shopper.id),
                'order_id': str(order.id),
                'correlation_id': str(order.id),
            }
        )
        
        if result.is_success():
            logger.info(f"Confirmação enviada: {result.message_id}")
        else:
            logger.error(f"Erro ao enviar: {result.error}")
        
        return result
```

## Exemplo 3: Novo Endpoint (Core_SinapUm)

Criar endpoint novo que usa gateway:

```python
# app_exemplo/api/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.services.whatsapp.gateway import get_whatsapp_gateway

@api_view(['POST'])
def send_notification(request):
    """POST /api/v1/notifications/send"""
    phone = request.data.get('phone')
    text = request.data.get('text')
    shopper_id = request.data.get('shopper_id')
    
    gateway = get_whatsapp_gateway()
    result = gateway.send_text(
        to=phone,
        text=text,
        metadata={'shopper_id': shopper_id}
    )
    
    return Response({
        'success': result.is_success(),
        'message_id': result.message_id,
        'provider': result.provider_name,
        'error': result.error
    })
```

## Exemplo 4: Teste sem WhatsApp Real

```python
# Em ambiente de desenvolvimento
import os
os.environ['WHATSAPP_GATEWAY_PROVIDER'] = 'noop'  # ou 'simulated'

from core.services.whatsapp.gateway import get_whatsapp_gateway

gateway = get_whatsapp_gateway()
result = gateway.send_text(
    to="5511999999999",
    text="Teste",
    metadata={'shopper_id': 'test'}
)

# NoOp: apenas loga
# Simulated: grava em SimulatedMessage
```

## Exemplo 5: Modo Shadow

```python
# Logar sem enviar (para testes em produção)
import os
os.environ['WHATSAPP_SHADOW_MODE'] = 'true'

gateway = get_whatsapp_gateway()
result = gateway.send_text(
    to="5511999999999",
    text="Teste",
    metadata={'shopper_id': 'test'}
)

# Resultado: status="sent" mas não envia realmente
# Logs são gerados normalmente
```

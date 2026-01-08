# Prompt Completo: Implementação WhatsApp Gateway

## 🎯 Prompt para Cursor/AI

```
Você é um engenheiro sênior Django/DRF + arquiteto de integração WhatsApp. 
Implemente no repositório **Core_SinapUm** um "WhatsApp Gateway" com **contrato único (IWhatsAppProvider)**, **eventos canônicos**, **providers plugáveis** e um **ProviderSimulado completo** para destravar o desenvolvimento do VitrineZap sem depender da Evolution API.

⚙️ PRINCÍPIO DE ARQUITETURA
- O Core_SinapUm expõe endpoints estáveis `/api/whatsapp/*`.
- O Core conversa com um provider ativo selecionado por env `WHATSAPP_PROVIDER`.
- O VitrineZap/Évora NUNCA chama Evolution diretamente; chama apenas o Core (Gateway).
- Tudo que acontece vira um **Evento Canônico** (persistido e logado).

══════════════════════════════════════════════════════════════════════
0) ESCOPO E NÃO-ESCOPO
✅ Fazer agora (Fase A):
- Criar app Django `app_whatsapp`
- Criar contrato `IWhatsAppProvider`
- Implementar ProviderSimulated (com QR fake e simulação completa de eventos)
- Criar Router de Provider por env
- Criar EventBus (persistência DB + logs)
- Criar endpoints DRF estáveis
- Incluir migrations + testes mínimos
- Incluir README curto do módulo

❌ Não fazer agora:
- Integração real com Evolution / Baileys / Cloud (apenas stubs com NotImplementedError e evento ERROR)
- Alterar endpoints existentes do Core sem necessidade
══════════════════════════════════════════════════════════════════════

1) ESTRUTURA DE PASTAS (criar exatamente assim)
Crie um app Django novo: `app_whatsapp/` com esta estrutura:

app_whatsapp/
  __init__.py
  apps.py
  admin.py

  domain/
    __init__.py
    provider_contract.py     # interface IWhatsAppProvider
    events.py                # enums/tipos + schema do evento canônico

  models.py                  # AppWhatsappEvent + AppWhatsappInstance
  migrations/
    __init__.py
    0001_initial.py

  providers/
    __init__.py
    base.py                  # helpers comuns
    provider_simulated.py
    provider_cloud.py        # stub
    provider_baileys.py      # stub
    provider_evolution.py    # stub (Fase B)

  services/
    __init__.py
    whatsapp_router.py       # escolhe provider ativo (singleton)
    event_bus.py             # persistência + logger + helpers
    instance_registry.py     # estado simples da instância p/ simulação

  api/
    __init__.py
    serializers.py
    views.py
    urls.py

  tests/
    __init__.py
    test_simulated_provider.py

══════════════════════════════════════════════════════════════════════
2) MODELO DE EVENTO CANÔNICO (OBRIGATÓRIO)
Crie o model `AppWhatsappEvent` em `app_whatsapp/models.py`:

Campos obrigatórios:
- id: UUIDField (primary_key=True, default=uuid.uuid4, editable=False)
- event_id: UUIDField (unique=True, default=uuid.uuid4)
- ts: DateTimeField (auto_now_add=True)
- provider: CharField (max_length=32, db_index=True)
- instance_key: CharField (max_length=128, db_index=True)
- type: CharField (max_length=64, db_index=True)  # EVENT TYPE
- shopper_id: CharField (max_length=128, null=True, blank=True, db_index=True)
- correlation_id: UUIDField (null=True, blank=True)
- data: JSONField (default=dict)

Meta:
- indexes: [('instance_key', 'ts'), ('provider', 'type'), ('shopper_id', 'ts')]
- ordering: ['-ts']

Crie também `AppWhatsappInstance`:
- instance_key: CharField (max_length=128, unique=True, primary_key=True)
- provider: CharField (max_length=32)
- status: CharField (max_length=32, choices=[('created', 'Created'), ('connecting', 'Connecting'), ('connected', 'Connected'), ('closed', 'Closed')], default='created')
- last_qr: TextField (null=True, blank=True)
- created_at: DateTimeField (auto_now_add=True)
- updated_at: DateTimeField (auto_now=True)

══════════════════════════════════════════════════════════════════════
3) ENUMS / TIPOS DE EVENTO
Em `domain/events.py`, defina:

```python
from enum import Enum
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from django.utils import timezone

class EventType(str, Enum):
    INSTANCE_CREATED = "INSTANCE_CREATED"
    QR_UPDATED = "QR_UPDATED"
    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    MESSAGE_IN = "MESSAGE_IN"
    MESSAGE_OUT = "MESSAGE_OUT"
    DELIVERY = "DELIVERY"
    ERROR = "ERROR"

def create_canonical_event(
    provider: str,
    instance_key: str,
    event_type: EventType,
    data: Dict[str, Any],
    shopper_id: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Cria payload canônico de evento"""
    return {
        "event_id": str(uuid4()),
        "ts": timezone.now().isoformat(),
        "provider": provider,
        "instance_key": instance_key,
        "type": event_type.value,
        "shopper_id": shopper_id,
        "correlation_id": correlation_id,
        "data": data,
    }
```

══════════════════════════════════════════════════════════════════════
4) CONTRATO ÚNICO IWhatsAppProvider
Em `domain/provider_contract.py`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from django.http import HttpRequest

class IWhatsAppProvider(ABC):
    """Contrato único para todos os providers WhatsApp"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do provider (simulated, cloud, baileys, evolution)"""
        pass
    
    @abstractmethod
    def create_instance(self, instance_key: str) -> Dict[str, Any]:
        """
        Cria uma nova instância WhatsApp.
        Retorna: {"success": bool, "instance_key": str, "status": str}
        Deve emitir evento INSTANCE_CREATED via EventBus.
        """
        pass
    
    @abstractmethod
    def get_qr(self, instance_key: str) -> Dict[str, Any]:
        """
        Obtém QR code da instância (se aplicável).
        Retorna: {"count": int, "qr_code": str, "base64": str (opcional)}
        Deve emitir evento QR_UPDATED se QR mudou.
        """
        pass
    
    @abstractmethod
    def send_message(
        self,
        instance_key: str,
        to: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Envia mensagem.
        payload: {"text": str, "media": dict (opcional), "buttons": list (opcional)}
        Retorna: {"success": bool, "message_id": str}
        Deve emitir evento MESSAGE_OUT via EventBus.
        """
        pass
    
    @abstractmethod
    def health(self) -> Dict[str, Any]:
        """
        Verifica saúde do provider.
        Retorna: {"status": "ok|error", "message": str}
        """
        pass
    
    @abstractmethod
    def handle_inbound_webhook(self, request: HttpRequest) -> Dict[str, Any]:
        """
        Processa webhook de entrada do provider.
        Retorna: {"success": bool, "events": list}
        Deve emitir eventos MESSAGE_IN, DELIVERY, etc via EventBus.
        """
        pass
```

══════════════════════════════════════════════════════════════════════
5) EVENT BUS (SERVIÇO CENTRAL)
Em `services/event_bus.py`:

```python
import logging
from typing import Dict, Any
from app_whatsapp.models import AppWhatsappEvent
from app_whatsapp.domain.events import create_canonical_event, EventType

logger = logging.getLogger(__name__)

class EventBus:
    """Publica eventos canônicos (DB + logs)"""
    
    @staticmethod
    def emit(
        provider: str,
        instance_key: str,
        event_type: EventType,
        data: Dict[str, Any],
        shopper_id: str = None,
        correlation_id: str = None,
    ) -> AppWhatsappEvent:
        """Emite evento canônico e persiste"""
        event_payload = create_canonical_event(
            provider=provider,
            instance_key=instance_key,
            event_type=event_type,
            data=data,
            shopper_id=shopper_id,
            correlation_id=correlation_id,
        )
        
        # Persistir no DB
        event = AppWhatsappEvent.objects.create(
            event_id=event_payload["event_id"],
            provider=provider,
            instance_key=instance_key,
            type=event_type.value,
            shopper_id=shopper_id,
            correlation_id=correlation_id,
            data=event_payload["data"],
        )
        
        # Logar
        logger.info(
            f"[WhatsApp Gateway] Event: {event_type.value} | "
            f"Provider: {provider} | Instance: {instance_key} | "
            f"Shopper: {shopper_id} | Data: {data}"
        )
        
        return event
```

══════════════════════════════════════════════════════════════════════
6) PROVIDER SIMULATED (IMPLEMENTAÇÃO COMPLETA)
Em `providers/provider_simulated.py`:

```python
import hashlib
import base64
from typing import Dict, Any, Optional
from django.http import HttpRequest
from app_whatsapp.domain.provider_contract import IWhatsAppProvider
from app_whatsapp.domain.events import EventType
from app_whatsapp.services.event_bus import EventBus
from app_whatsapp.models import AppWhatsappInstance

class ProviderSimulated(IWhatsAppProvider):
    """Provider simulado para desenvolvimento sem WhatsApp real"""
    
    @property
    def name(self) -> str:
        return "simulated"
    
    def create_instance(self, instance_key: str) -> Dict[str, Any]:
        """Cria instância simulada (sempre conectável)"""
        instance, created = AppWhatsappInstance.objects.get_or_create(
            instance_key=instance_key,
            defaults={
                "provider": self.name,
                "status": "connecting",
            }
        )
        
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.INSTANCE_CREATED,
            data={"status": instance.status},
        )
        
        return {
            "success": True,
            "instance_key": instance_key,
            "status": instance.status,
        }
    
    def get_qr(self, instance_key: str) -> Dict[str, Any]:
        """Gera QR fake determinístico"""
        try:
            instance = AppWhatsappInstance.objects.get(instance_key=instance_key)
        except AppWhatsappInstance.DoesNotExist:
            return {"count": 0, "qr_code": None}
        
        # QR fake baseado no instance_key (determinístico)
        qr_data = f"SIMULATED_QR_{instance_key}"
        qr_hash = hashlib.md5(qr_data.encode()).hexdigest()
        qr_code = base64.b64encode(qr_hash.encode()).decode()[:32]
        
        instance.last_qr = qr_code
        instance.save()
        
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.QR_UPDATED,
            data={"qr_code": qr_code, "count": 1},
        )
        
        return {
            "count": 1,
            "qr_code": qr_code,
            "base64": f"data:image/png;base64,{qr_code}",
        }
    
    def send_message(
        self,
        instance_key: str,
        to: str,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Simula envio de mensagem"""
        message_id = f"sim_{hashlib.md5(f'{instance_key}{to}'.encode()).hexdigest()[:16]}"
        
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.MESSAGE_OUT,
            data={
                "to": to,
                "message_id": message_id,
                "payload": payload,
            },
            correlation_id=correlation_id,
        )
        
        return {
            "success": True,
            "message_id": message_id,
        }
    
    def health(self) -> Dict[str, Any]:
        return {"status": "ok", "message": "Simulated provider is always healthy"}
    
    def handle_inbound_webhook(self, request: HttpRequest) -> Dict[str, Any]:
        """Simulado não usa webhook real"""
        return {"success": False, "message": "Simulated provider does not use webhooks"}
    
    def simulate_scan(self, instance_key: str) -> Dict[str, Any]:
        """Método especial: simula escaneamento do QR"""
        try:
            instance = AppWhatsappInstance.objects.get(instance_key=instance_key)
            instance.status = "connected"
            instance.save()
            
            EventBus.emit(
                provider=self.name,
                instance_key=instance_key,
                event_type=EventType.CONNECTED,
                data={"status": "connected"},
            )
            
            return {"success": True, "status": "connected"}
        except AppWhatsappInstance.DoesNotExist:
            return {"success": False, "error": "Instance not found"}
    
    def simulate_disconnect(self, instance_key: str) -> Dict[str, Any]:
        """Método especial: simula desconexão"""
        try:
            instance = AppWhatsappInstance.objects.get(instance_key=instance_key)
            instance.status = "closed"
            instance.save()
            
            EventBus.emit(
                provider=self.name,
                instance_key=instance_key,
                event_type=EventType.DISCONNECTED,
                data={"status": "closed"},
            )
            
            return {"success": True, "status": "closed"}
        except AppWhatsappInstance.DoesNotExist:
            return {"success": False, "error": "Instance not found"}
    
    def simulate_inbound_message(
        self,
        instance_key: str,
        from_number: str,
        text: str,
        shopper_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Método especial: simula mensagem recebida"""
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.MESSAGE_IN,
            data={
                "from": from_number,
                "text": text,
            },
            shopper_id=shopper_id,
        )
        
        return {
            "success": True,
            "message": "Inbound message simulated",
        }
```

══════════════════════════════════════════════════════════════════════
7) PROVIDER ROUTER
Em `services/whatsapp_router.py`:

```python
import os
from typing import Optional
from django.conf import settings
from app_whatsapp.domain.provider_contract import IWhatsAppProvider
from app_whatsapp.providers.provider_simulated import ProviderSimulated
from app_whatsapp.providers.provider_cloud import ProviderCloud
from app_whatsapp.providers.provider_baileys import ProviderBaileys
from app_whatsapp.providers.provider_evolution import ProviderEvolution

class WhatsAppRouter:
    """Router singleton que retorna provider ativo"""
    
    _instance: Optional['WhatsAppRouter'] = None
    _provider: Optional[IWhatsAppProvider] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_provider(self) -> IWhatsAppProvider:
        """Retorna provider ativo baseado em WHATSAPP_PROVIDER"""
        if self._provider is None:
            provider_name = os.getenv(
                'WHATSAPP_PROVIDER',
                getattr(settings, 'WHATSAPP_PROVIDER', 'simulated')
            ).lower()
            
            if provider_name == 'simulated':
                self._provider = ProviderSimulated()
            elif provider_name == 'cloud':
                self._provider = ProviderCloud()
            elif provider_name == 'baileys':
                self._provider = ProviderBaileys()
            elif provider_name == 'evolution':
                self._provider = ProviderEvolution()
            else:
                raise ValueError(f"Unknown provider: {provider_name}")
        
        return self._provider
```

══════════════════════════════════════════════════════════════════════
8) STUBS DOS OUTROS PROVIDERS
Em `providers/provider_cloud.py`, `provider_baileys.py`, `provider_evolution.py`:

```python
from typing import Dict, Any, Optional
from django.http import HttpRequest
from app_whatsapp.domain.provider_contract import IWhatsAppProvider
from app_whatsapp.domain.events import EventType
from app_whatsapp.services.event_bus import EventBus

class ProviderCloud(IWhatsAppProvider):
    """Stub para Cloud API (Fase A2)"""
    
    @property
    def name(self) -> str:
        return "cloud"
    
    def create_instance(self, instance_key: str) -> Dict[str, Any]:
        EventBus.emit(
            provider=self.name,
            instance_key=instance_key,
            event_type=EventType.ERROR,
            data={"error": "Provider cloud not implemented yet"},
        )
        raise NotImplementedError("Cloud provider not implemented")
    
    # ... implementar todos os métodos com NotImplementedError
```

══════════════════════════════════════════════════════════════════════
9) SERIALIZERS (DRF)
Em `api/serializers.py`:

```python
from rest_framework import serializers

class InstanceCreateSerializer(serializers.Serializer):
    instance_key = serializers.CharField(max_length=128)

class SendMessageSerializer(serializers.Serializer):
    instance_key = serializers.CharField(max_length=128)
    to = serializers.CharField(max_length=32)
    payload = serializers.DictField()
    correlation_id = serializers.UUIDField(required=False)

class SimulateInboundSerializer(serializers.Serializer):
    from_number = serializers.CharField(max_length=32)
    text = serializers.CharField()
    shopper_id = serializers.CharField(max_length=128, required=False)
```

══════════════════════════════════════════════════════════════════════
10) VIEWS (DRF)
Em `api/views.py`:

```python
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpRequest
from app_whatsapp.services.whatsapp_router import WhatsAppRouter
from app_whatsapp.api.serializers import (
    InstanceCreateSerializer,
    SendMessageSerializer,
    SimulateInboundSerializer,
)

@api_view(['POST'])
@permission_classes([AllowAny])  # Ajustar permissões conforme necessário
def create_instance(request):
    """POST /api/whatsapp/instances/"""
    serializer = InstanceCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    router = WhatsAppRouter()
    provider = router.get_provider()
    result = provider.create_instance(serializer.validated_data['instance_key'])
    
    return Response(result, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_qr(request, instance_key):
    """GET /api/whatsapp/instances/{instance_key}/qr/"""
    router = WhatsAppRouter()
    provider = router.get_provider()
    result = provider.get_qr(instance_key)
    
    return Response(result)

@api_view(['POST'])
@permission_classes([AllowAny])
def send_message(request):
    """POST /api/whatsapp/send/"""
    serializer = SendMessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    router = WhatsAppRouter()
    provider = router.get_provider()
    result = provider.send_message(
        instance_key=serializer.validated_data['instance_key'],
        to=serializer.validated_data['to'],
        payload=serializer.validated_data['payload'],
        correlation_id=serializer.validated_data.get('correlation_id'),
    )
    
    return Response(result)

@api_view(['POST'])
@permission_classes([AllowAny])
def inbound_webhook(request):
    """POST /api/whatsapp/inbound/"""
    router = WhatsAppRouter()
    provider = router.get_provider()
    result = provider.handle_inbound_webhook(request)
    
    return Response(result)

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """GET /api/whatsapp/health/"""
    router = WhatsAppRouter()
    provider = router.get_provider()
    result = provider.health()
    
    return Response(result)

# Endpoints de simulação (apenas para ProviderSimulated)
@api_view(['POST'])
@permission_classes([AllowAny])
def simulate_scan(request, instance_key):
    """POST /api/whatsapp/instances/{instance_key}/simulate/scan/"""
    router = WhatsAppRouter()
    provider = router.get_provider()
    
    if provider.name != 'simulated':
        return Response(
            {"error": "Simulation endpoints only available for simulated provider"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = provider.simulate_scan(instance_key)
    return Response(result)

@api_view(['POST'])
@permission_classes([AllowAny])
def simulate_disconnect(request, instance_key):
    """POST /api/whatsapp/instances/{instance_key}/simulate/disconnect/"""
    router = WhatsAppRouter()
    provider = router.get_provider()
    
    if provider.name != 'simulated':
        return Response(
            {"error": "Simulation endpoints only available for simulated provider"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = provider.simulate_disconnect(instance_key)
    return Response(result)

@api_view(['POST'])
@permission_classes([AllowAny])
def simulate_inbound(request, instance_key):
    """POST /api/whatsapp/instances/{instance_key}/simulate/inbound/"""
    serializer = SimulateInboundSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    router = WhatsAppRouter()
    provider = router.get_provider()
    
    if provider.name != 'simulated':
        return Response(
            {"error": "Simulation endpoints only available for simulated provider"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    result = provider.simulate_inbound_message(
        instance_key=instance_key,
        from_number=serializer.validated_data['from_number'],
        text=serializer.validated_data['text'],
        shopper_id=serializer.validated_data.get('shopper_id'),
    )
    
    return Response(result)
```

══════════════════════════════════════════════════════════════════════
11) URLS
Em `api/urls.py`:

```python
from django.urls import path
from app_whatsapp.api import views

app_name = 'whatsapp'

urlpatterns = [
    path('instances/', views.create_instance, name='create_instance'),
    path('instances/<str:instance_key>/qr/', views.get_qr, name='get_qr'),
    path('instances/<str:instance_key>/simulate/scan/', views.simulate_scan, name='simulate_scan'),
    path('instances/<str:instance_key>/simulate/disconnect/', views.simulate_disconnect, name='simulate_disconnect'),
    path('instances/<str:instance_key>/simulate/inbound/', views.simulate_inbound, name='simulate_inbound'),
    path('send/', views.send_message, name='send_message'),
    path('inbound/', views.inbound_webhook, name='inbound_webhook'),
    path('health/', views.health, name='health'),
]
```

No `urls.py` principal do Core_SinapUm, adicionar:

```python
urlpatterns = [
    # ... outras URLs
    path('api/whatsapp/', include('app_whatsapp.api.urls')),
]
```

══════════════════════════════════════════════════════════════════════
12) ADMIN
Em `admin.py`:

```python
from django.contrib import admin
from app_whatsapp.models import AppWhatsappEvent, AppWhatsappInstance

@admin.register(AppWhatsappEvent)
class AppWhatsappEventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'ts', 'provider', 'instance_key', 'type', 'shopper_id']
    list_filter = ['provider', 'type', 'ts']
    search_fields = ['instance_key', 'shopper_id', 'event_id']
    readonly_fields = ['event_id', 'ts']

@admin.register(AppWhatsappInstance)
class AppWhatsappInstanceAdmin(admin.ModelAdmin):
    list_display = ['instance_key', 'provider', 'status', 'created_at', 'updated_at']
    list_filter = ['provider', 'status']
    search_fields = ['instance_key']
```

══════════════════════════════════════════════════════════════════════
13) APPS.PY
Em `apps.py`:

```python
from django.apps import AppConfig

class AppWhatsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_whatsapp'
    verbose_name = 'WhatsApp Gateway'
```

══════════════════════════════════════════════════════════════════════
14) TESTES MÍNIMOS
Em `tests/test_simulated_provider.py`:

```python
from django.test import TestCase
from app_whatsapp.providers.provider_simulated import ProviderSimulated
from app_whatsapp.models import AppWhatsappEvent, AppWhatsappInstance
from app_whatsapp.domain.events import EventType

class ProviderSimulatedTestCase(TestCase):
    def setUp(self):
        self.provider = ProviderSimulated()
        self.instance_key = "test_instance_123"
    
    def test_create_instance(self):
        result = self.provider.create_instance(self.instance_key)
        self.assertTrue(result['success'])
        self.assertEqual(result['instance_key'], self.instance_key)
        
        # Verificar evento criado
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.INSTANCE_CREATED.value
        ).first()
        self.assertIsNotNone(event)
    
    def test_get_qr(self):
        self.provider.create_instance(self.instance_key)
        result = self.provider.get_qr(self.instance_key)
        
        self.assertEqual(result['count'], 1)
        self.assertIsNotNone(result['qr_code'])
        
        # Verificar evento QR_UPDATED
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.QR_UPDATED.value
        ).first()
        self.assertIsNotNone(event)
    
    def test_simulate_scan(self):
        self.provider.create_instance(self.instance_key)
        result = self.provider.simulate_scan(self.instance_key)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['status'], 'connected')
        
        instance = AppWhatsappInstance.objects.get(instance_key=self.instance_key)
        self.assertEqual(instance.status, 'connected')
    
    def test_simulate_inbound_message(self):
        self.provider.create_instance(self.instance_key)
        result = self.provider.simulate_inbound_message(
            instance_key=self.instance_key,
            from_number="5511999999999",
            text="Olá",
            shopper_id="shopper_123"
        )
        
        self.assertTrue(result['success'])
        
        # Verificar evento MESSAGE_IN
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.MESSAGE_IN.value
        ).first()
        self.assertIsNotNone(event)
        self.assertEqual(event.shopper_id, "shopper_123")
    
    def test_send_message(self):
        self.provider.create_instance(self.instance_key)
        result = self.provider.send_message(
            instance_key=self.instance_key,
            to="5511999999999",
            payload={"text": "Teste"},
        )
        
        self.assertTrue(result['success'])
        self.assertIn('message_id', result)
        
        # Verificar evento MESSAGE_OUT
        event = AppWhatsappEvent.objects.filter(
            instance_key=self.instance_key,
            type=EventType.MESSAGE_OUT.value
        ).first()
        self.assertIsNotNone(event)
```

══════════════════════════════════════════════════════════════════════
15) SETTINGS.PY
Adicionar app em `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... outros apps
    'app_whatsapp',
]
```

Adicionar variável de ambiente (opcional):

```python
WHATSAPP_PROVIDER = os.getenv('WHATSAPP_PROVIDER', 'simulated')
```

══════════════════════════════════════════════════════════════════════
16) README DO MÓDULO
Criar `app_whatsapp/README.md`:

```markdown
# WhatsApp Gateway

Gateway plugável para integração WhatsApp com providers múltiplos.

## Providers

- **simulated**: Provider simulado para desenvolvimento (padrão)
- **cloud**: WhatsApp Cloud API (Fase A2)
- **baileys**: Baileys direto (Fase A2)
- **evolution**: Evolution API (Fase B)

## Configuração

```bash
export WHATSAPP_PROVIDER=simulated
```

## Endpoints

- `POST /api/whatsapp/instances/` - Criar instância
- `GET /api/whatsapp/instances/{key}/qr/` - Obter QR
- `POST /api/whatsapp/send/` - Enviar mensagem
- `POST /api/whatsapp/inbound/` - Webhook universal
- `GET /api/whatsapp/health/` - Health check

## Simulação (apenas simulated)

- `POST /api/whatsapp/instances/{key}/simulate/scan/` - Simular scan QR
- `POST /api/whatsapp/instances/{key}/simulate/disconnect/` - Simular desconexão
- `POST /api/whatsapp/instances/{key}/simulate/inbound/` - Simular mensagem recebida

## Eventos

Todos os eventos são persistidos em `AppWhatsappEvent` e logados.

Tipos: INSTANCE_CREATED, QR_UPDATED, CONNECTED, DISCONNECTED, MESSAGE_IN, MESSAGE_OUT, DELIVERY, ERROR
```

══════════════════════════════════════════════════════════════════════
17) CRITÉRIOS DE SUCESSO

Após implementação, validar:

✅ `python manage.py migrate` cria tabelas
✅ `POST /api/whatsapp/instances/ {"instance_key": "test"}` retorna 201
✅ `GET /api/whatsapp/instances/test/qr/` retorna count>0 e qr_code
✅ `POST /api/whatsapp/instances/test/simulate/scan/` muda status para connected
✅ `POST /api/whatsapp/instances/test/simulate/inbound/` emite MESSAGE_IN
✅ `POST /api/whatsapp/send/` emite MESSAGE_OUT
✅ Eventos aparecem em `AppWhatsappEvent` no admin
✅ Logs aparecem no console
✅ Testes passam: `python manage.py test app_whatsapp`

══════════════════════════════════════════════════════════════════════

Implemente agora, escrevendo todos os arquivos necessários com código completo, importações corretas, e seguindo as convenções Django/DRF.
```

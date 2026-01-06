"""
Views DRF para WhatsApp Gateway
"""
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
        correlation_id=str(serializer.validated_data.get('correlation_id')) if serializer.validated_data.get('correlation_id') else None,
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

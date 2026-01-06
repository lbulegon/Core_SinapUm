"""
Serializers DRF para WhatsApp Gateway
"""
from rest_framework import serializers


class InstanceCreateSerializer(serializers.Serializer):
    """Serializer para criar instância"""
    instance_key = serializers.CharField(max_length=128)


class SendMessageSerializer(serializers.Serializer):
    """Serializer para enviar mensagem"""
    instance_key = serializers.CharField(max_length=128)
    to = serializers.CharField(max_length=32)
    payload = serializers.DictField()
    correlation_id = serializers.UUIDField(required=False, allow_null=True)


class SimulateInboundSerializer(serializers.Serializer):
    """Serializer para simular mensagem recebida"""
    from_number = serializers.CharField(max_length=32)
    text = serializers.CharField()
    shopper_id = serializers.CharField(max_length=128, required=False, allow_blank=True)

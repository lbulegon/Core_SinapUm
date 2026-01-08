#!/usr/bin/env python
"""
Script de Smoke Test - Webhook Evolution
=========================================

Testa o fluxo completo:
1. Envia payload fake de webhook Evolution
2. Verifica se Conversation foi criada
3. Verifica se Message foi criada
4. Verifica se Suggestion foi criada (se OpenMind habilitado)

Uso:
    python scripts/smoke_test_evolution_webhook.py
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_whatsapp_gateway.models import EvolutionInstance
from app_conversations.models import Conversation, Message, Suggestion
from app_whatsapp_gateway.views import webhook_receiver
from django.test import RequestFactory


def test_webhook():
    """Testa webhook Evolution"""
    print("🧪 Testando webhook Evolution...")
    
    # Criar instância de teste
    shopper_id = "test_shopper_123"
    instance_id = "test_instance_123"
    
    instance, created = EvolutionInstance.objects.get_or_create(
        shopper_id=shopper_id,
        instance_id=instance_id,
        defaults={
            'status': EvolutionInstance.InstanceStatus.OPEN,
        }
    )
    print(f"✅ Instância criada/obtida: {instance.instance_id}")
    
    # Criar payload fake
    payload = {
        "event": "messages.upsert",
        "instance": instance_id,
        "data": {
            "key": {
                "remoteJid": "5511999999999@s.whatsapp.net",
                "id": "test_msg_123"
            },
            "message": {
                "conversation": "Olá, quero comprar um produto"
            },
            "messageTimestamp": int(datetime.now().timestamp() * 1000)
        }
    }
    
    # Simular request
    factory = RequestFactory()
    request = factory.post(
        f'/webhooks/evolution/{instance_id}/messages',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    # Processar webhook
    response = webhook_receiver(request, instance_id)
    print(f"✅ Webhook processado: {response.status_code}")
    
    # Verificar Conversation criada
    conversation = Conversation.objects.filter(
        shopper_id=shopper_id,
        conversation_key__contains="5511999999999"
    ).first()
    
    if conversation:
        print(f"✅ Conversation criada: {conversation.id}")
        
        # Verificar Message criada
        message = Message.objects.filter(conversation=conversation).first()
        if message:
            print(f"✅ Message criada: {message.id}")
            print(f"   Texto: {message.text}")
        else:
            print("❌ Message NÃO criada")
    else:
        print("❌ Conversation NÃO criada")
    
    # Verificar Suggestion (se OpenMind habilitado)
    from django.conf import settings
    if getattr(settings, 'FEATURE_OPENMIND_ENABLED', False):
        suggestion = Suggestion.objects.filter(conversation=conversation).first()
        if suggestion:
            print(f"✅ Suggestion criada: {suggestion.id}")
            print(f"   Resposta sugerida: {suggestion.suggested_reply[:50]}...")
        else:
            print("⚠️  Suggestion não criada (OpenMind pode não estar respondendo)")
    
    print("\n✅ Teste concluído!")


if __name__ == '__main__':
    test_webhook()


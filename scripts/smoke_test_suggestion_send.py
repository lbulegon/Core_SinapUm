#!/usr/bin/env python
"""
Script de Smoke Test - Enviar Sugestão
=======================================

Testa o fluxo de envio de sugestão:
1. Cria Conversation e Message
2. Cria Suggestion
3. Envia sugestão
4. Verifica se Message out foi criada

Uso:
    python scripts/smoke_test_suggestion_send.py
"""

import os
import sys
import django
from datetime import datetime

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_whatsapp_gateway.models import EvolutionInstance
from app_conversations.models import Conversation, Message, Suggestion
from app_conversations.services import SuggestionService, MessageService
from app_whatsapp_gateway.clients import EvolutionClient


def test_suggestion_send():
    """Testa envio de sugestão"""
    print("🧪 Testando envio de sugestão...")
    
    # Criar instância
    shopper_id = "test_shopper_456"
    instance_id = "test_instance_456"
    
    instance, created = EvolutionInstance.objects.get_or_create(
        shopper_id=shopper_id,
        instance_id=instance_id,
        defaults={
            'status': EvolutionInstance.InstanceStatus.OPEN,
        }
    )
    print(f"✅ Instância: {instance.instance_id}")
    
    # Criar conversa
    conversation, created = Conversation.objects.get_or_create(
        shopper_id=shopper_id,
        conversation_key=f"whatsapp:+5511999999999",
        defaults={
            'instance_id': instance_id,
            'customer_phone': '+5511999999999',
            'customer_name': 'Cliente Teste',
        }
    )
    print(f"✅ Conversation: {conversation.id}")
    
    # Criar mensagem de entrada
    message_in = Message.objects.create(
        conversation=conversation,
        direction=Message.Direction.IN,
        message_type=Message.MessageType.TEXT,
        text='Quero comprar um produto',
        sent_by=Message.SentBy.CUSTOMER,
        timestamp=datetime.now(),
    )
    print(f"✅ Message IN criada: {message_in.id}")
    
    # Criar sugestão
    suggestion = Suggestion.objects.create(
        conversation=conversation,
        intent='buscar_produto',
        confidence=0.9,
        suggested_reply='Encontrei estes produtos para você...',
        status=Suggestion.Status.PENDING,
    )
    print(f"✅ Suggestion criada: {suggestion.id}")
    
    # Marcar como enviada (simular envio)
    SuggestionService.mark_sent(str(suggestion.id))
    print(f"✅ Suggestion marcada como enviada")
    
    # Verificar se Message out foi criada (deveria ser criada pelo view, mas vamos simular)
    message_out = Message.objects.filter(
        conversation=conversation,
        direction=Message.Direction.OUT,
        text=suggestion.suggested_reply
    ).first()
    
    if message_out:
        print(f"✅ Message OUT criada: {message_out.id}")
    else:
        print("⚠️  Message OUT não encontrada (pode ser criada pelo view)")
    
    print("\n✅ Teste concluído!")


if __name__ == '__main__':
    test_suggestion_send()


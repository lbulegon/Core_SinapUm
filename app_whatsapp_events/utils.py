"""
Utils - WhatsApp Events
=======================

Funções utilitárias para persistência e roteamento de eventos.
"""
import hashlib
import uuid
import logging
from typing import Optional, Dict, Any, Union
from django.db import transaction
from django.utils import timezone

from .models import (
    WhatsAppEventLog,
    WhatsAppConversation,
    WhatsAppThreadParticipant,
    WhatsAppMessageIndex,
)

logger = logging.getLogger(__name__)


def generate_idempotency_key(
    provider: str,
    provider_message_id: Optional[str] = None,
    provider_event_id: Optional[str] = None,
    occurred_at: Optional[timezone.datetime] = None
) -> str:
    """
    Gera chave de idempotência determinística
    
    Args:
        provider: Nome do provider
        provider_message_id: ID da mensagem no provider
        provider_event_id: ID do evento no provider
        occurred_at: Timestamp do evento
    
    Returns:
        Chave de idempotência (hash)
    """
    # Usar provider_message_id se disponível (mais confiável)
    if provider_message_id:
        key_parts = [provider, provider_message_id]
    elif provider_event_id:
        key_parts = [provider, provider_event_id]
    else:
        # Fallback: usar timestamp + provider (menos confiável)
        timestamp_str = occurred_at.isoformat() if occurred_at else timezone.now().isoformat()
        key_parts = [provider, timestamp_str]
    
    key_string = "|".join(key_parts)
    return hashlib.sha256(key_string.encode()).hexdigest()


def generate_thread_key(
    chat_type: str,
    wa_id: Optional[str] = None,
    group_id: Optional[str] = None,
    shopper_id: Optional[str] = None
) -> str:
    """
    Gera chave de thread determinística
    
    Formato:
    - Private: whatsapp:{customer_wa_id}|shopper:{shopper_id}|group:null
    - Group: whatsapp:group:{group_id}|shopper:{shopper_id}
    
    Args:
        chat_type: Tipo de chat (private, group)
        wa_id: WhatsApp ID do cliente (para private)
        group_id: ID do grupo (para group)
        shopper_id: ID do shopper
    
    Returns:
        Chave do thread
    """
    if chat_type == "private" and wa_id:
        return f"whatsapp:{wa_id}|shopper:{shopper_id or 'null'}|group:null"
    elif chat_type == "group" and group_id:
        return f"whatsapp:group:{group_id}|shopper:{shopper_id or 'null'}"
    else:
        # Fallback
        return f"whatsapp:{chat_type}:{wa_id or group_id or 'unknown'}|shopper:{shopper_id or 'null'}"


def get_or_create_conversation(
    thread_key: str,
    shopper_id: Optional[str] = None,
    skm_id: Optional[str] = None,
    keeper_id: Optional[str] = None,
    conversation_id: Optional[str] = None
) -> WhatsAppConversation:
    """
    Obtém ou cria uma conversação baseada no thread_key
    
    Args:
        thread_key: Chave do thread (determinística)
        shopper_id: ID do shopper
        skm_id: ID do SKM
        keeper_id: ID do keeper
        conversation_id: ID da conversação (se já existir)
    
    Returns:
        WhatsAppConversation
    """
    if conversation_id:
        try:
            return WhatsAppConversation.objects.get(conversation_id=conversation_id)
        except WhatsAppConversation.DoesNotExist:
            pass
    
    conversation, created = WhatsAppConversation.objects.get_or_create(
        thread_key=thread_key,
        defaults={
            'conversation_id': conversation_id or str(uuid.uuid4()),
            'shopper_id': shopper_id,
            'skm_id': skm_id,
            'keeper_id': keeper_id,
            'status': 'open',
        }
    )
    
    if created:
        logger.info(f"Conversação criada: {conversation.conversation_id} (thread: {thread_key})")
    else:
        # Atualizar metadados se necessário
        updated = False
        if shopper_id and not conversation.shopper_id:
            conversation.shopper_id = shopper_id
            updated = True
        if skm_id and not conversation.skm_id:
            conversation.skm_id = skm_id
            updated = True
        if keeper_id and not conversation.keeper_id:
            conversation.keeper_id = keeper_id
            updated = True
        
        if updated:
            conversation.save()
    
    return conversation


def append_event(
    event_envelope: Union[Dict[str, Any], Any],
    persist_message_index: bool = True
) -> WhatsAppEventLog:
    """
    Adiciona evento ao log e atualiza conversação
    
    Args:
        event_envelope: EventEnvelope (dict ou objeto Pydantic)
        persist_message_index: Se True, cria índice de mensagem (default: True)
    
    Returns:
        WhatsAppEventLog criado
    
    Raises:
        IntegrityError: Se evento já existe (idempotência)
    """
    # Converter envelope para dict se necessário
    if hasattr(event_envelope, 'to_dict'):
        event_envelope = event_envelope.to_dict()
    elif hasattr(event_envelope, 'dict'):
        event_envelope = event_envelope.dict()
    elif not isinstance(event_envelope, dict):
        raise ValueError("event_envelope deve ser dict ou objeto Pydantic")
    
    # Extrair dados do envelope
    event_id = event_envelope.get('event_id')
    event_type = event_envelope.get('event_type')
    occurred_at = event_envelope.get('occurred_at')
    source = event_envelope.get('source', {})
    routing = event_envelope.get('routing', {})
    actor = event_envelope.get('actor', {})
    context = event_envelope.get('context', {})
    message = event_envelope.get('message', {})
    trace = event_envelope.get('trace', {})
    security = event_envelope.get('security', {})
    raw = event_envelope.get('raw', {})
    
    # Gerar idempotency_key se não fornecido
    idempotency_key = trace.get('idempotency_key')
    if not idempotency_key:
        idempotency_key = generate_idempotency_key(
            provider=source.get('provider', 'unknown'),
            provider_message_id=source.get('provider_message_id'),
            provider_event_id=source.get('provider_event_id'),
            occurred_at=occurred_at
        )
    
    # Verificar idempotência
    if WhatsAppEventLog.objects.filter(idempotency_key=idempotency_key).exists():
        existing = WhatsAppEventLog.objects.get(idempotency_key=idempotency_key)
        logger.debug(f"Evento já existe (idempotência): {idempotency_key}")
        return existing
    
    # Gerar thread_key se não fornecido
    thread_key = routing.get('thread_key')
    if not thread_key:
        thread_key = generate_thread_key(
            chat_type=context.get('chat_type', 'private'),
            wa_id=actor.get('wa_id'),
            group_id=context.get('group', {}).get('id') if context.get('group') else None,
            shopper_id=routing.get('shopper_id')
        )
    
    with transaction.atomic():
        # Obter ou criar conversação
        conversation = get_or_create_conversation(
            thread_key=thread_key,
            shopper_id=routing.get('shopper_id'),
            skm_id=routing.get('skm_id'),
            keeper_id=routing.get('keeper_id'),
            conversation_id=routing.get('conversation_id')
        )
        
        # Criar evento
        event_log = WhatsAppEventLog.objects.create(
            event_id=event_id,
            event_type=event_type,
            event_version=event_envelope.get('event_version', '1.0'),
            occurred_at=occurred_at or timezone.now(),
            provider=source.get('provider', 'unknown'),
            provider_account_id=source.get('provider_account_id'),
            provider_message_id=source.get('provider_message_id'),
            webhook_id=source.get('webhook_id'),
            idempotency_key=idempotency_key,
            correlation_id=trace.get('correlation_id'),
            parent_event_id=trace.get('parent_event_id'),
            shopper_id=routing.get('shopper_id'),
            skm_id=routing.get('skm_id'),
            keeper_id=routing.get('keeper_id'),
            conversation_id=conversation.conversation_id,
            thread_key=thread_key,
            actor_wa_id=actor.get('wa_id'),
            actor_role=actor.get('role'),
            chat_type=context.get('chat_type'),
            group_id=context.get('group', {}).get('id') if context.get('group') else None,
            message_type=message.get('type'),
            message_direction=message.get('direction'),
            payload_json=event_envelope.get('payload_json', {}),
            raw_provider_payload=raw,
            signature_valid=security.get('signature_valid', True),
            risk_flags=security.get('risk_flags', []),
        )
        
        # Atualizar conversação
        conversation.last_event_at = event_log.occurred_at
        conversation.last_actor_wa_id = actor.get('wa_id')
        if conversation.status == 'closed':
            conversation.status = 'open'  # Reabrir se receber novo evento
        conversation.save()
        
        # Criar/atualizar participante
        if actor.get('wa_id'):
            participant, _ = WhatsAppThreadParticipant.objects.get_or_create(
                conversation=conversation,
                wa_id=actor.get('wa_id'),
                defaults={
                    'role': actor.get('role', 'customer'),
                    'display_name': actor.get('display_name'),
                }
            )
            participant.last_seen_at = event_log.occurred_at
            if actor.get('role'):
                participant.role = actor.get('role')
            participant.save()
        
        # Criar índice de mensagem se aplicável
        if persist_message_index and message.get('message_id') and source.get('provider_message_id'):
            WhatsAppMessageIndex.objects.get_or_create(
                provider_message_id=source.get('provider_message_id'),
                defaults={
                    'message_id': event_id,
                    'conversation': conversation,
                    'direction': message.get('direction', 'inbound'),
                    'message_type': message.get('type', 'text'),
                    'occurred_at': event_log.occurred_at,
                }
            )
        
        logger.info(f"Evento adicionado: {event_id} (type: {event_type}, thread: {thread_key})")
        return event_log

"""
Normalizer - WhatsApp Canonical Events v1.0
============================================

Normaliza eventos de diferentes providers para o formato canônico v1.0.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from django.conf import settings

from .schemas import (
    EventEnvelope,
    EventType,
    EventSource,
    MessagePayload,
    MediaPayload,
    LocationPayload,
    ContactPayload,
    ButtonPayload,
    ListPayload,
    StatusPayload,
)

logger = logging.getLogger(__name__)


class EventNormalizer:
    """
    Normalizador de eventos WhatsApp
    
    Converte payloads brutos de diferentes providers para EventEnvelope v1.0.
    """
    
    def normalize(
        self,
        provider: str,
        raw_payload: Dict[str, Any],
        instance_key: Optional[str] = None
    ) -> Optional[EventEnvelope]:
        """
        Normaliza payload bruto para EventEnvelope canônico
        
        Args:
            provider: Nome do provider (evolution, cloud, baileys, simulated)
            raw_payload: Payload bruto do webhook
            instance_key: Chave da instância (opcional)
        
        Returns:
            EventEnvelope canônico ou None se não conseguir normalizar
        """
        try:
            provider_lower = provider.lower()
            
            if provider_lower == 'evolution':
                return self._normalize_evolution(raw_payload, instance_key)
            elif provider_lower == 'cloud':
                return self._normalize_cloud(raw_payload, instance_key)
            elif provider_lower == 'baileys':
                return self._normalize_baileys(raw_payload, instance_key)
            elif provider_lower == 'simulated':
                return self._normalize_simulated(raw_payload, instance_key)
            else:
                logger.warning(f"Provider desconhecido: {provider}")
                return self._normalize_unknown(raw_payload, instance_key, provider)
        
        except Exception as e:
            logger.error(f"Erro ao normalizar evento de {provider}: {e}", exc_info=True)
            return None
    
    def _normalize_evolution(
        self,
        payload: Dict[str, Any],
        instance_key: Optional[str]
    ) -> Optional[EventEnvelope]:
        """Normaliza evento do Evolution API"""
        event_type = payload.get('event')
        data = payload.get('data', {})
        
        # Mapear tipos de evento Evolution para canônico
        event_type_map = {
            'messages.upsert': EventType.MESSAGE_TEXT,
            'messages.update': EventType.MESSAGE_SENT,
            'connection.update': EventType.INSTANCE_CONNECTION_UPDATE,
            'qr': EventType.INSTANCE_QR_UPDATED,
        }
        
        canonical_type = event_type_map.get(event_type, EventType.WEBHOOK_RECEIVED)
        
        # Extrair informações básicas
        key = data.get('key', {})
        message = data.get('message', {})
        
        from_number = key.get('remoteJid', '').replace('@s.whatsapp.net', '').replace('@c.us', '')
        message_id = key.get('id')
        instance_key = instance_key or payload.get('instance', 'default')
        
        # Construir payload específico
        canonical_payload = None
        if canonical_type == EventType.MESSAGE_TEXT:
            text = message.get('conversation') or message.get('extendedTextMessage', {}).get('text', '')
            canonical_payload = MessagePayload(
                text=text,
                quoted_message_id=message.get('extendedTextMessage', {}).get('contextInfo', {}).get('quotedMessage', {}).get('key', {}).get('id')
            )
        elif canonical_type == EventType.MESSAGE_MEDIA:
            media_message = message.get('imageMessage') or message.get('videoMessage') or message.get('audioMessage') or message.get('documentMessage')
            if media_message:
                canonical_payload = MediaPayload(
                    media_type=self._detect_media_type(message),
                    media_url=media_message.get('url'),
                    media_id=media_message.get('mediaKey'),
                    caption=media_message.get('caption'),
                    mime_type=media_message.get('mimetype'),
                    file_size=media_message.get('fileLength'),
                    file_name=media_message.get('fileName'),
                )
        
        return EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type=canonical_type,
            event_source=EventSource.EVOLUTION,
            instance_key=instance_key,
            timestamp=datetime.fromtimestamp(data.get('messageTimestamp', datetime.now().timestamp())),
            from_number=from_number,
            message_id=message_id,
            payload=canonical_payload,
            provider_event_id=payload.get('id'),
            provider_message_id=message_id,
            raw={'provider': 'evolution', 'provider_payload': payload}
        )
    
    def _normalize_cloud(
        self,
        payload: Dict[str, Any],
        instance_key: Optional[str]
    ) -> Optional[EventEnvelope]:
        """Normaliza evento do WhatsApp Cloud API"""
        entry = payload.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        
        # Verificar se é mensagem
        messages = value.get('messages', [])
        statuses = value.get('statuses', [])
        
        if messages:
            message = messages[0]
            message_type = message.get('type')
            from_number = message.get('from')
            message_id = message.get('id')
            
            # Mapear tipo de mensagem
            if message_type == 'text':
                canonical_type = EventType.MESSAGE_TEXT
                canonical_payload = MessagePayload(text=message.get('text', {}).get('body', ''))
            elif message_type in ['image', 'video', 'audio', 'document']:
                canonical_type = EventType.MESSAGE_MEDIA
                media_data = message.get(message_type, {})
                canonical_payload = MediaPayload(
                    media_type=message_type,
                    media_id=media_data.get('id'),
                    caption=media_data.get('caption'),
                    mime_type=media_data.get('mime_type'),
                )
            else:
                canonical_type = EventType.WEBHOOK_RECEIVED
                canonical_payload = None
            
            return EventEnvelope(
                event_id=str(uuid.uuid4()),
                event_type=canonical_type,
                event_source=EventSource.CLOUD,
                instance_key=instance_key or 'default',
                timestamp=datetime.fromtimestamp(int(message.get('timestamp', 0))),
                from_number=from_number,
                message_id=message_id,
                payload=canonical_payload,
                provider_message_id=message_id,
                raw={'provider': 'cloud', 'provider_payload': payload}
            )
        
        elif statuses:
            status = statuses[0]
            return EventEnvelope(
                event_id=str(uuid.uuid4()),
                event_type=EventType.MESSAGE_DELIVERED,  # Cloud API não diferencia delivered/read
                event_source=EventSource.CLOUD,
                instance_key=instance_key or 'default',
                timestamp=datetime.fromtimestamp(int(status.get('timestamp', 0))),
                message_id=status.get('id'),
                payload=StatusPayload(
                    status=status.get('status', 'delivered'),
                    message_id=status.get('id'),
                ),
                provider_message_id=status.get('id'),
                raw={'provider': 'cloud', 'provider_payload': payload}
            )
        
        return None
    
    def _normalize_baileys(
        self,
        payload: Dict[str, Any],
        instance_key: Optional[str]
    ) -> Optional[EventEnvelope]:
        """Normaliza evento do Baileys"""
        # Baileys tem estrutura similar ao Evolution
        # Reutilizar lógica do Evolution
        return self._normalize_evolution(payload, instance_key)
    
    def _normalize_simulated(
        self,
        payload: Dict[str, Any],
        instance_key: Optional[str]
    ) -> Optional[EventEnvelope]:
        """Normaliza evento simulado (para testes)"""
        return EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type=EventType.MESSAGE_TEXT,
            event_source=EventSource.SIMULATED,
            instance_key=instance_key or 'simulated',
            timestamp=datetime.now(),
            from_number=payload.get('from'),
            to_number=payload.get('to'),
            message_id=payload.get('message_id'),
            payload=MessagePayload(text=payload.get('text', '')),
            raw={'provider': 'simulated', 'provider_payload': payload}
        )
    
    def _normalize_unknown(
        self,
        payload: Dict[str, Any],
        instance_key: Optional[str],
        provider: str
    ) -> Optional[EventEnvelope]:
        """Normaliza evento de provider desconhecido (genérico)"""
        return EventEnvelope(
            event_id=str(uuid.uuid4()),
            event_type=EventType.WEBHOOK_RECEIVED,
            event_source=EventSource.UNKNOWN,
            instance_key=instance_key or 'unknown',
            timestamp=datetime.now(),
            payload=None,
            raw={'provider': provider, 'provider_payload': payload}
        )
    
    def _detect_media_type(self, message: Dict[str, Any]) -> str:
        """Detecta tipo de mídia em mensagem Evolution"""
        if 'imageMessage' in message:
            return 'image'
        elif 'videoMessage' in message:
            return 'video'
        elif 'audioMessage' in message:
            return 'audio'
        elif 'documentMessage' in message:
            return 'document'
        return 'unknown'


# Singleton
_normalizer_instance: Optional[EventNormalizer] = None


def get_event_normalizer() -> EventNormalizer:
    """Obtém instância singleton do normalizador"""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = EventNormalizer()
    return _normalizer_instance

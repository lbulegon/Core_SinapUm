# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway.parsers.evolution_parser
# ============================================================================
# Parser de eventos Evolution API → Evento Canônico
# ============================================================================

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class EvolutionParser:
    """
    Parser de eventos Evolution API para Evento Canônico
    
    Converte payloads da Evolution API em formato canônico padronizado.
    """
    
    @staticmethod
    def parse_webhook(payload: Dict[str, Any], instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse webhook da Evolution API para Evento Canônico
        
        Args:
            payload: Payload completo do webhook
            instance_id: ID da instância que recebeu o evento
        
        Returns:
            Evento Canônico ou None se não for evento de mensagem
        """
        event = payload.get('event')
        event_data = payload.get('data', {})
        
        # Processar apenas eventos de mensagens
        if event != 'messages.upsert':
            return None
        
        try:
            key = event_data.get('key', {})
            remote_jid = key.get('remoteJid', '')
            message_id = key.get('id', '')
            
            # Extrair número do JID (formato: 5511999999999@s.whatsapp.net)
            phone = remote_jid.split('@')[0] if '@' in remote_jid else remote_jid
            
            # Determinar se é grupo
            is_group = '@g.us' in remote_jid
            chat_type = 'group' if is_group else 'private'
            
            # Extrair mensagem
            message_obj = event_data.get('message', {})
            message_text = None
            message_type = 'text'
            media_url = None
            
            if 'conversation' in message_obj:
                message_text = message_obj['conversation']
                message_type = 'text'
            elif 'extendedTextMessage' in message_obj:
                message_text = message_obj['extendedTextMessage'].get('text', '')
                message_type = 'text'
            elif 'imageMessage' in message_obj:
                message_type = 'image'
                message_text = message_obj['imageMessage'].get('caption', '')
                # Evolution pode retornar URL ou base64
                media_url = message_obj['imageMessage'].get('url') or None
            elif 'videoMessage' in message_obj:
                message_type = 'video'
                message_text = message_obj['videoMessage'].get('caption', '')
                media_url = message_obj['videoMessage'].get('url') or None
            elif 'audioMessage' in message_obj:
                message_type = 'audio'
                media_url = message_obj['audioMessage'].get('url') or None
            elif 'documentMessage' in message_obj:
                message_type = 'file'
                message_text = message_obj['documentMessage'].get('fileName', '')
                media_url = message_obj['documentMessage'].get('url') or None
            
            if not message_text and not media_url:
                # Mensagem sem conteúdo útil
                return None
            
            # Timestamp
            timestamp_ms = event_data.get('messageTimestamp', 0)
            if timestamp_ms:
                timestamp = datetime.fromtimestamp(timestamp_ms / 1000)
            else:
                from django.utils import timezone
                timestamp = timezone.now()
            
            # Construir Evento Canônico
            canonical_event = {
                'tenant_id': None,  # Será preenchido pelo service
                'shopper_id': None,  # Será preenchido pelo service
                'instance_id': instance_id,
                'conversation_id': None,  # Será preenchido pelo service
                'conversation_key': f"whatsapp:{phone}" if not is_group else f"whatsapp_group:{remote_jid}",
                'from_phone': phone,
                'chat_type': chat_type,
                'message_type': message_type,
                'text': message_text or '',
                'media': media_url,
                'timestamp': timestamp.isoformat(),
                'raw': payload,
            }
            
            return canonical_event
            
        except Exception as e:
            logger.error(f"Erro ao parsear webhook Evolution: {e}", exc_info=True)
            return None
    
    @staticmethod
    def parse_qrcode_event(payload: Dict[str, Any], instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Parse evento de QR Code atualizado
        
        Args:
            payload: Payload do webhook
            instance_id: ID da instância
        
        Returns:
            {
                'instance_id': str,
                'qrcode': str (base64),
                'qrcode_url': str (opcional)
            } ou None
        """
        event = payload.get('event')
        if event not in ['qrcode.updated', 'QRCODE_UPDATED']:
            return None
        
        event_data = payload.get('data', {})
        
        # Tentar diferentes formatos
        qrcode_data = event_data.get('qrcode', {}) or event_data.get('data', {}) or event_data
        
        if isinstance(qrcode_data, dict):
            qrcode_base64 = qrcode_data.get('base64') or qrcode_data.get('qrcode') or qrcode_data.get('code')
            qrcode_url = qrcode_data.get('url')
            
            if qrcode_base64:
                return {
                    'instance_id': instance_id,
                    'qrcode': qrcode_base64,
                    'qrcode_url': qrcode_url,
                }
        
        return None


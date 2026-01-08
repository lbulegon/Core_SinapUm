# ============================================================================
# WebSocket Service para Evolution API
# ============================================================================
# Service para gerenciar conexões WebSocket e processar eventos de QR code
# ============================================================================

import logging
import threading
from typing import Dict, Any, Optional, Callable
from django.utils import timezone

from ..models import EvolutionInstance
from ..clients.websocket_client import EvolutionWebSocketClient, start_websocket_listener

logger = logging.getLogger(__name__)


class WebSocketService:
    """
    Service para gerenciar WebSocket connections da Evolution API
    """
    
    def __init__(self):
        self.active_connections = {}  # {instance_id: (client, thread)}
    
    def start_listening_for_instance(self, instance_id: str) -> bool:
        """
        Inicia listener WebSocket para uma instância
        
        Args:
            instance_id: ID da instância
        
        Returns:
            True se iniciado com sucesso
        """
        if instance_id in self.active_connections:
            logger.info(f"WebSocket já está ativo para {instance_id}")
            return True
        
        try:
            # Handler para eventos de QR code
            def handle_qrcode_event(event_data: Dict[str, Any]):
                """Processa evento de QR code atualizado"""
                try:
                    instance = EvolutionInstance.objects.get(instance_id=instance_id)
                    
                    # Extrair QR code do evento
                    qrcode_data = event_data.get('data', {}) or event_data.get('qrcode', {})
                    
                    if isinstance(qrcode_data, dict):
                        qrcode_base64 = (
                            qrcode_data.get('base64') or 
                            qrcode_data.get('qrcode') or 
                            qrcode_data.get('code')
                        )
                        qrcode_url = qrcode_data.get('url')
                        
                        if qrcode_base64:
                            # Atualizar instância no banco
                            instance.qrcode = qrcode_base64
                            if qrcode_url:
                                instance.qrcode_url = qrcode_url
                            instance.status = EvolutionInstance.InstanceStatus.CONNECTING
                            instance.last_sync = timezone.now()
                            instance.save()
                            
                            logger.info(f"QR code atualizado via WebSocket para {instance_id}")
                except EvolutionInstance.DoesNotExist:
                    logger.warning(f"Instância {instance_id} não encontrada ao processar evento WebSocket")
                except Exception as e:
                    logger.error(f"Erro ao processar evento de QR code: {e}", exc_info=True)
            
            # Handler para eventos de conexão
            def handle_connection_event(event_data: Dict[str, Any]):
                """Processa evento de atualização de conexão"""
                try:
                    instance = EvolutionInstance.objects.get(instance_id=instance_id)
                    
                    status = event_data.get('data', {}).get('state') or event_data.get('state')
                    phone_number = event_data.get('data', {}).get('phone', {}).get('number')
                    phone_name = event_data.get('data', {}).get('phone', {}).get('name')
                    
                    if status:
                        status_map = {
                            'open': EvolutionInstance.InstanceStatus.OPEN,
                            'close': EvolutionInstance.InstanceStatus.CLOSE,
                            'connecting': EvolutionInstance.InstanceStatus.CONNECTING,
                            'unpaired': EvolutionInstance.InstanceStatus.UNPAIRED,
                        }
                        
                        instance.status = status_map.get(status, EvolutionInstance.InstanceStatus.UNKNOWN)
                        
                        if phone_number:
                            instance.phone_number = phone_number
                        if phone_name:
                            instance.phone_name = phone_name
                        
                        instance.last_sync = timezone.now()
                        instance.save()
                        
                        logger.info(f"Status atualizado via WebSocket para {instance_id}: {status}")
                except Exception as e:
                    logger.error(f"Erro ao processar evento de conexão: {e}", exc_info=True)
            
            # Iniciar listener
            client, thread = start_websocket_listener(
                instance_id,
                qrcode_handler=handle_qrcode_event
            )
            
            # Registrar handlers adicionais
            client.register_handler('connection.update', handle_connection_event)
            client.register_handler('CONNECTION_UPDATE', handle_connection_event)
            
            self.active_connections[instance_id] = (client, thread)
            logger.info(f"WebSocket listener iniciado para {instance_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao iniciar WebSocket listener: {e}", exc_info=True)
            return False
    
    def stop_listening_for_instance(self, instance_id: str):
        """
        Para listener WebSocket para uma instância
        
        Args:
            instance_id: ID da instância
        """
        if instance_id in self.active_connections:
            client, thread = self.active_connections[instance_id]
            try:
                # Desconectar (precisa ser em thread separada ou async)
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(client.disconnect())
                loop.close()
            except Exception as e:
                logger.error(f"Erro ao desconectar WebSocket: {e}")
            
            del self.active_connections[instance_id]
            logger.info(f"WebSocket listener parado para {instance_id}")
    
    def is_listening(self, instance_id: str) -> bool:
        """
        Verifica se está ouvindo eventos para uma instância
        
        Args:
            instance_id: ID da instância
        
        Returns:
            True se está ouvindo
        """
        return instance_id in self.active_connections


# Instância global do service
websocket_service = WebSocketService()

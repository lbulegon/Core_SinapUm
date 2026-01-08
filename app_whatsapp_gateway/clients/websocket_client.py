# ============================================================================
# WebSocket Client para Evolution API
# ============================================================================
# Cliente WebSocket para receber eventos em tempo real da Evolution API
# Incluindo eventos de QR code (qrcode.updated)
# ============================================================================

import asyncio
import json
import logging
import websockets
from typing import Dict, Any, Optional, Callable
from django.conf import settings

logger = logging.getLogger(__name__)


class EvolutionWebSocketClient:
    """
    Cliente WebSocket para Evolution API
    
    Recebe eventos em tempo real, incluindo:
    - qrcode.updated: Quando QR code é gerado/atualizado
    - connection.update: Quando status de conexão muda
    - messages.upsert: Quando mensagens são recebidas
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa cliente WebSocket
        
        Args:
            base_url: URL base da Evolution API (default: EVOLUTION_BASE_URL)
            api_key: Chave API da Evolution (default: EVOLUTION_API_KEY)
        """
        self.base_url = base_url or getattr(settings, 'EVOLUTION_BASE_URL', 'http://69.169.102.84:8004')
        self.api_key = api_key or getattr(settings, 'EVOLUTION_API_KEY', '')
        
        # Converter http:// para ws://
        ws_url = self.base_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.ws_url = f"{ws_url}/instance/connect"
        
        self.connected = False
        self.websocket = None
        self.event_handlers = {}
        
    def on_event(self, event_type: str):
        """
        Decorator para registrar handler de evento
        
        Args:
            event_type: Tipo de evento (ex: 'qrcode.updated', 'connection.update')
        
        Usage:
            @client.on_event('qrcode.updated')
            def handle_qrcode(event_data):
                print(f"QR code atualizado: {event_data}")
        """
        def decorator(handler: Callable):
            if event_type not in self.event_handlers:
                self.event_handlers[event_type] = []
            self.event_handlers[event_type].append(handler)
            return handler
        return decorator
    
    def register_handler(self, event_type: str, handler: Callable):
        """
        Registra handler para um tipo de evento
        
        Args:
            event_type: Tipo de evento
            handler: Função que recebe (event_data: Dict) -> None
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def _handle_message(self, message: str):
        """
        Processa mensagem recebida do WebSocket
        
        Args:
            message: Mensagem JSON recebida
        """
        try:
            data = json.loads(message)
            event_type = data.get('event') or data.get('eventType') or 'unknown'
            
            logger.debug(f"Evento WebSocket recebido: {event_type}")
            
            # Chamar handlers registrados para este tipo de evento
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Erro ao executar handler para {event_type}: {e}", exc_info=True)
            
            # Handler genérico para todos os eventos
            if 'all' in self.event_handlers:
                for handler in self.event_handlers['all']:
                    try:
                        handler(data)
                    except Exception as e:
                        logger.error(f"Erro ao executar handler genérico: {e}", exc_info=True)
                        
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar mensagem WebSocket: {e}")
        except Exception as e:
            logger.error(f"Erro ao processar mensagem WebSocket: {e}", exc_info=True)
    
    async def connect(self, instance_id: str):
        """
        Conecta ao WebSocket da Evolution API
        
        Args:
            instance_id: ID da instância para conectar
        
        Returns:
            True se conectado com sucesso
        """
        try:
            # URL do WebSocket com instance_id e API key
            url = f"{self.ws_url}/{instance_id}?apikey={self.api_key}"
            
            logger.info(f"Conectando ao WebSocket: {url}")
            
            self.websocket = await websockets.connect(
                url,
                extra_headers={
                    'apikey': self.api_key,
                }
            )
            
            self.connected = True
            logger.info(f"Conectado ao WebSocket para instância {instance_id}")
            
            # Iniciar loop de recebimento de mensagens
            async for message in self.websocket:
                await self._handle_message(message)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Conexão WebSocket fechada")
            self.connected = False
        except Exception as e:
            logger.error(f"Erro ao conectar WebSocket: {e}", exc_info=True)
            self.connected = False
            raise
    
    async def disconnect(self):
        """Desconecta do WebSocket"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Desconectado do WebSocket")
    
    def start_listening(self, instance_id: str, loop: Optional[asyncio.AbstractEventLoop] = None):
        """
        Inicia listener em thread separada (para uso síncrono)
        
        Args:
            instance_id: ID da instância
            loop: Event loop (opcional)
        """
        if loop is None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self.connect(instance_id))
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
        finally:
            loop.run_until_complete(self.disconnect())
            loop.close()


# Função helper para uso síncrono
def start_websocket_listener(instance_id: str, qrcode_handler: Optional[Callable] = None):
    """
    Inicia listener WebSocket para uma instância
    
    Args:
        instance_id: ID da instância
        qrcode_handler: Função para processar eventos de QR code
                       Recebe (event_data: Dict) -> None
    
    Usage:
        def handle_qrcode(event_data):
            qrcode = event_data.get('data', {}).get('qrcode', {})
            if isinstance(qrcode, dict):
                base64 = qrcode.get('base64')
                if base64:
                    print(f"QR code recebido: {base64[:50]}...")
        
        start_websocket_listener('instance_123', handle_qrcode)
    """
    client = EvolutionWebSocketClient()
    
    if qrcode_handler:
        client.register_handler('qrcode.updated', qrcode_handler)
        client.register_handler('QRCODE_UPDATED', qrcode_handler)
    
    # Executar em thread separada
    import threading
    thread = threading.Thread(
        target=client.start_listening,
        args=(instance_id,),
        daemon=True
    )
    thread.start()
    
    return client, thread

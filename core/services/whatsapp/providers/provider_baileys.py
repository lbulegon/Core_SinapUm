"""
Provider Baileys - Integração com Baileys Service
===================================================

Provider que usa o Baileys Service para envio de mensagens WhatsApp.
Equivalente ao projeto Node.js bot-do-mago, mas integrado ao gateway do Core_SinapUm.
"""
import logging
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth
from ...baileys_service import BaileysClient
from ...baileys_service.exceptions import (
    BaileysConnectionError,
    BaileysAuthError,
    BaileysMessageError
)

logger = logging.getLogger(__name__)


class ProviderBaileys(IWhatsAppProvider):
    """
    Provider Baileys para WhatsApp
    
    Usa o Baileys Service (Python) para enviar mensagens WhatsApp.
    Equivalente funcional ao projeto Node.js bot-do-mago.
    """
    
    _client: Optional[BaileysClient] = None
    _session_name: str = "vitrinezap-baileys"
    
    def __init__(self, session_name: Optional[str] = None):
        """
        Inicializa provider Baileys
        
        Args:
            session_name: Nome da sessão (opcional, padrão: vitrinezap-baileys)
        """
        if session_name:
            self._session_name = session_name
    
    @property
    def name(self) -> str:
        return "baileys"
    
    def _get_client(self) -> BaileysClient:
        """
        Obtém ou cria cliente Baileys (singleton)
        
        Returns:
            Instância do BaileysClient
        """
        if self._client is None:
            self._client = BaileysClient(session_name=self._session_name)
        
        return self._client
    
    async def _ensure_connected(self):
        """Garante que cliente está conectado"""
        client = self._get_client()
        
        if not client.is_connected:
            try:
                await client.connect()
            except BaileysConnectionError as e:
                logger.error(f"Erro ao conectar Baileys: {e}")
                raise
            except BaileysAuthError as e:
                logger.error(f"Erro de autenticação Baileys: {e}")
                raise
    
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia mensagem de texto via Baileys
        
        Args:
            to: Número de destino (formato: 5511999999999 ou +5511999999999)
            text: Texto da mensagem
            metadata: Metadados adicionais
        
        Returns:
            ProviderResult com resultado da operação
        """
        try:
            # Remove caracteres não numéricos do número
            to_clean = ''.join(filter(str.isdigit, to))
            if to_clean.startswith('55'):  # Brasil
                to_clean = to_clean
            elif to_clean.startswith('0'):
                to_clean = '55' + to_clean[1:]
            else:
                to_clean = '55' + to_clean
            
            # Executa envio assíncrono
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Se loop já está rodando, cria task
                task = asyncio.create_task(self._send_text_async(to_clean, text))
                # Aguarda resultado (com timeout)
                try:
                    result = loop.run_until_complete(asyncio.wait_for(task, timeout=30.0))
                except asyncio.TimeoutError:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error="Timeout ao enviar mensagem",
                        metadata=metadata or {}
                    )
            else:
                # Se loop não está rodando, executa diretamente
                result = loop.run_until_complete(self._send_text_async(to_clean, text))
            
            return ProviderResult(
                provider_name=self.name,
                status="sent",
                message_id=result.get('message_id'),
                raw=result,
                metadata=metadata or {}
            )
            
        except BaileysConnectionError as e:
            logger.error(f"Erro de conexão Baileys: {e}")
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=f"Erro de conexão: {str(e)}",
                metadata=metadata or {}
            )
        except BaileysMessageError as e:
            logger.error(f"Erro ao enviar mensagem Baileys: {e}")
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=f"Erro ao enviar mensagem: {str(e)}",
                metadata=metadata or {}
            )
        except Exception as e:
            logger.error(f"Erro inesperado no provider Baileys: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=f"Erro inesperado: {str(e)}",
                metadata=metadata or {}
            )
    
    async def _send_text_async(self, to: str, text: str) -> Dict[str, Any]:
        """Envia mensagem de texto (método assíncrono interno)"""
        await self._ensure_connected()
        client = self._get_client()
        return await client.send_text(to, text)
    
    def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """
        Envia mídia via Baileys
        
        Args:
            to: Número de destino
            media_url: URL da mídia (ou caminho local)
            caption: Legenda (opcional)
            metadata: Metadados adicionais
        
        Returns:
            ProviderResult com resultado da operação
        """
        try:
            # Remove caracteres não numéricos do número
            to_clean = ''.join(filter(str.isdigit, to))
            if to_clean.startswith('55'):  # Brasil
                to_clean = to_clean
            elif to_clean.startswith('0'):
                to_clean = '55' + to_clean[1:]
            else:
                to_clean = '55' + to_clean
            
            # Determina se é URL ou caminho local
            if media_url.startswith('http://') or media_url.startswith('https://'):
                # URL - precisa baixar primeiro
                import requests
                response = requests.get(media_url, timeout=30)
                media_path = Path('/tmp') / f"baileys_media_{datetime.now().timestamp()}"
                media_path.write_bytes(response.content)
            else:
                # Caminho local
                media_path = Path(media_url)
                if not media_path.exists():
                    raise ValueError(f"Arquivo não encontrado: {media_url}")
            
            # Determina tipo de mídia
            media_type = self._detect_media_type(media_path)
            
            # Executa envio assíncrono
            loop = asyncio.get_event_loop()
            if loop.is_running():
                task = asyncio.create_task(
                    self._send_media_async(to_clean, str(media_path), media_type, caption)
                )
                try:
                    result = loop.run_until_complete(asyncio.wait_for(task, timeout=60.0))
                except asyncio.TimeoutError:
                    return ProviderResult(
                        provider_name=self.name,
                        status="failed",
                        error="Timeout ao enviar mídia",
                        metadata=metadata or {}
                    )
            else:
                result = loop.run_until_complete(
                    self._send_media_async(to_clean, str(media_path), media_type, caption)
                )
            
            return ProviderResult(
                provider_name=self.name,
                status="sent",
                message_id=result.get('message_id'),
                raw=result,
                metadata=metadata or {}
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar mídia Baileys: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=f"Erro ao enviar mídia: {str(e)}",
                metadata=metadata or {}
            )
    
    async def _send_media_async(
        self,
        to: str,
        media_path: str,
        media_type: str,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia mídia (método assíncrono interno)"""
        await self._ensure_connected()
        client = self._get_client()
        
        if media_type == "image":
            return await client.send_image(to, media_path, caption)
        elif media_type == "document":
            return await client.send_document(to, media_path, caption)
        else:
            # Default: documento
            return await client.send_document(to, media_path, caption)
    
    def _detect_media_type(self, file_path: Path) -> str:
        """Detecta tipo de mídia pelo arquivo"""
        ext = file_path.suffix.lower()
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        
        if ext in image_extensions:
            return "image"
        elif ext in video_extensions:
            return "video"
        else:
            return "document"
    
    def healthcheck(self) -> ProviderHealth:
        """
        Verifica saúde do provider Baileys
        
        Returns:
            ProviderHealth com status do provider
        """
        try:
            client = self._get_client()
            
            if client.is_connected:
                return ProviderHealth(
                    provider_name=self.name,
                    status="healthy",
                    message="Baileys conectado e operacional",
                    last_check=datetime.now(),
                    metadata={
                        'session_name': self._session_name,
                        'connected': True
                    }
                )
            else:
                return ProviderHealth(
                    provider_name=self.name,
                    status="degraded",
                    message="Baileys não está conectado",
                    last_check=datetime.now(),
                    metadata={
                        'session_name': self._session_name,
                        'connected': False
                    }
                )
                
        except Exception as e:
            logger.error(f"Erro no healthcheck Baileys: {e}", exc_info=True)
            return ProviderHealth(
                provider_name=self.name,
                status="unhealthy",
                message=f"Erro no healthcheck: {str(e)}",
                last_check=datetime.now()
            )

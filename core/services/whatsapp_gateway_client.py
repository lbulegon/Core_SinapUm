"""
WhatsApp Gateway Client - Cliente Python para WhatsApp Gateway Service
========================================================================

Cliente para comunicação com o serviço WhatsApp Gateway (Node.js + Baileys).
"""
import logging
import os
import requests
from typing import Optional, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class WhatsAppGatewayClient:
    """
    Cliente para WhatsApp Gateway Service
    
    Comunica com o serviço Node.js que gerencia conexão WhatsApp via Baileys.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Inicializa cliente
        
        Args:
            base_url: URL base do serviço (padrão: SINAPUM_WHATSAPP_GATEWAY_URL)
            api_key: API Key para autenticação (padrão: SINAPUM_WHATSAPP_GATEWAY_API_KEY)
        """
        # Lê de os.environ primeiro (variáveis do Docker), depois tenta settings, depois default
        self.base_url = (
            base_url 
            or os.environ.get('SINAPUM_WHATSAPP_GATEWAY_URL')
            or getattr(settings, 'SINAPUM_WHATSAPP_GATEWAY_URL', None)
            or 'http://whatsapp_gateway_service:8007'
        )
        
        self.api_key = (
            api_key
            or os.environ.get('SINAPUM_WHATSAPP_GATEWAY_API_KEY')
            or getattr(settings, 'SINAPUM_WHATSAPP_GATEWAY_API_KEY', None)
        )
        
        if not self.api_key:
            logger.warning("SINAPUM_WHATSAPP_GATEWAY_API_KEY não configurada")
    
    def _get_headers(self) -> Dict[str, str]:
        """Retorna headers para requisições"""
        headers = {
            'Content-Type': 'application/json',
        }
        if self.api_key:
            headers['X-API-Key'] = self.api_key
            logger.debug(f"API Key configurada: {self.api_key[:10]}... (base_url: {self.base_url})")
        else:
            logger.warning("API Key não configurada - requisições podem falhar")
        return headers
    
    def healthcheck(self) -> Dict[str, Any]:
        """
        Verifica saúde do serviço
        
        Returns:
            Dicionário com status do serviço
        """
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro no healthcheck: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Obtém status da conexão WhatsApp
        
        Returns:
            Dicionário com status da conexão
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/status",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            raise
    
    def get_qr_code(self) -> Optional[bytes]:
        """
        Obtém QR code para autenticação
        
        Returns:
            Bytes da imagem do QR code ou None
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/qr",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.content
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
        except Exception as e:
            logger.error(f"Erro ao obter QR code: {e}")
            raise
    
    def connect(self) -> Dict[str, Any]:
        """
        Inicia conexão WhatsApp
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/connect",
                headers=self._get_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}")
            raise
    
    def disconnect(self) -> Dict[str, Any]:
        """
        Desconecta WhatsApp
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/disconnect",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao desconectar: {e}")
            raise
    
    def reset_session(self) -> Dict[str, Any]:
        """
        Reseta sessão WhatsApp (remove autenticação)
        
        Returns:
            Dicionário com resultado da operação
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/session/reset",
                headers=self._get_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao resetar sessão: {e}")
            raise
    
    def send_text(self, to: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        
        Args:
            to: Número de destino (formato: 5511999999999)
            text: Texto da mensagem
        
        Returns:
            Dicionário com resultado (message_id, status, etc.)
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/send/text",
                headers=self._get_headers(),
                json={
                    'to': to,
                    'text': text,
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            raise
    
    def send_image(
        self,
        to: str,
        image_path: Optional[str] = None,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia imagem
        
        Args:
            to: Número de destino
            image_path: Caminho local da imagem
            image_url: URL da imagem
            image_base64: Imagem em base64
            caption: Legenda (opcional)
        
        Returns:
            Dicionário com resultado
        """
        try:
            payload = {
                'to': to,
            }
            
            if image_path:
                payload['image_path'] = image_path
            elif image_url:
                payload['image_url'] = image_url
            elif image_base64:
                payload['image_base64'] = image_base64
            else:
                raise ValueError("É necessário fornecer image_path, image_url ou image_base64")
            
            if caption:
                payload['caption'] = caption
            
            response = requests.post(
                f"{self.base_url}/v1/send/image",
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar imagem: {e}")
            raise
    
    def send_document(
        self,
        to: str,
        document_path: Optional[str] = None,
        document_url: Optional[str] = None,
        document_base64: Optional[str] = None,
        filename: Optional[str] = None,
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Envia documento
        
        Args:
            to: Número de destino
            document_path: Caminho local do documento
            document_url: URL do documento
            document_base64: Documento em base64
            filename: Nome do arquivo (opcional)
            caption: Legenda (opcional)
        
        Returns:
            Dicionário com resultado
        """
        try:
            payload = {
                'to': to,
            }
            
            if document_path:
                payload['document_path'] = document_path
            elif document_url:
                payload['document_url'] = document_url
            elif document_base64:
                payload['document_base64'] = document_base64
            else:
                raise ValueError("É necessário fornecer document_path, document_url ou document_base64")
            
            if filename:
                payload['filename'] = filename
            if caption:
                payload['caption'] = caption
            
            response = requests.post(
                f"{self.base_url}/v1/send/document",
                headers=self._get_headers(),
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro ao enviar documento: {e}")
            raise


# Instância singleton
_client_instance = None


def get_whatsapp_gateway_client() -> WhatsAppGatewayClient:
    """
    Obtém instância singleton do cliente
    
    Returns:
        Instância do WhatsAppGatewayClient
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = WhatsAppGatewayClient()
    return _client_instance

# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway.clients.evolution_client
# ============================================================================
# Cliente Evolution API - Multi-tenant por instance_id
# 
# ANTIGO: EvolutionAPIService (Évora) - instância única
# NOVO: EvolutionClient (Core) - multi-tenant por instance_id
# ============================================================================

import requests
import logging
import time
from typing import Dict, Optional, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class EvolutionClient:
    """
    Cliente Evolution API - Multi-tenant
    
    DIFERENÇA DO ANTIGO:
    - Antigo: Usa instance_name (string) e assume instância única
    - Novo: Usa instance_id (string) e suporta múltiplas instâncias por shopper
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Inicializa cliente Evolution API
        
        Args:
            base_url: URL base da Evolution API (default: EVOLUTION_BASE_URL)
            api_key: Chave API da Evolution (default: EVOLUTION_API_KEY)
        """
        self.base_url = base_url or getattr(settings, 'EVOLUTION_BASE_URL', 'http://69.169.102.84:8004')
        self.api_key = api_key or getattr(settings, 'EVOLUTION_API_KEY', '')
        self.timeout = getattr(settings, 'EVOLUTION_TIMEOUT', 30)
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key,
        }
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, raise_on_error: bool = True) -> Dict[str, Any]:
        """
        Faz requisição HTTP para Evolution API
        
        Args:
            method: Método HTTP (GET, POST, PUT, DELETE)
            endpoint: Endpoint da API (ex: '/instance/create')
            data: Dados para enviar (opcional)
            raise_on_error: Se True, levanta exceção em caso de erro HTTP
        
        Returns:
            Resposta da API como dict
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=self.timeout
            )
            
            if raise_on_error:
                response.raise_for_status()
            
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erro HTTP ao fazer requisição para Evolution API {endpoint}: {e}")
            if response.status_code == 404:
                return {'success': False, 'error': 'Endpoint não encontrado', 'status_code': 404}
            return {'success': False, 'error': str(e), 'status_code': response.status_code}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao fazer requisição para Evolution API: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_instance(self, instance_id: str, qrcode: bool = True) -> Dict[str, Any]:
        """
        Cria nova instância Evolution
        
        Args:
            instance_id: ID da instância (ex: 'shopper_123')
            qrcode: Se True, tenta obter QR code após criar
        
        Returns:
            {
                'success': bool,
                'instance': {...},
                'qrcode': '...' (se qrcode=True e disponível)
            }
        """
        endpoint = '/instance/create'
        data = {
            'instanceName': instance_id,
            'qrcode': qrcode,
            'integration': 'WHATSAPP-BAILEYS',
        }
        
        result = self._request('POST', endpoint, data)
        
        # Se criação foi bem-sucedida mas não veio QR code, tentar obter
        if result.get('success') or (not result.get('error') and result.get('instance')):
            # Aguardar um pouco para a instância inicializar
            time.sleep(2)
            
            # Tentar obter QR code
            if qrcode:
                qr_result = self.get_qr(instance_id)
                if qr_result.get('qrcode'):
                    result['qrcode'] = qr_result.get('qrcode')
                    result['qrcode_url'] = qr_result.get('qrcode_url')
        
        return result
    
    def get_qr(self, instance_id: str, retry: bool = True) -> Dict[str, Any]:
        """
        Obtém QR Code da instância
        
        Tenta múltiplos endpoints e formatos de resposta para obter o QR code.
        
        Args:
            instance_id: ID da instância
            retry: Se True, tenta novamente após aguardar se não encontrar QR code
        
        Returns:
            {
                'success': bool,
                'qrcode': 'data:image/png;base64,...' ou base64 direto,
                'qrcode_url': 'https://...' (opcional)
            }
        """
        # Tentar endpoint principal primeiro
        endpoint = f'/instance/connect/{instance_id}'
        result = self._request('GET', endpoint, raise_on_error=False)
        
        # Verificar se retornou QR code em diferentes formatos
        qrcode_data = self._extract_qrcode_from_response(result)
        if qrcode_data:
            return {
                'success': True,
                'qrcode': qrcode_data.get('qrcode'),
                'qrcode_url': qrcode_data.get('qrcode_url'),
            }
        
        # Se retornou {"count": 0}, o QR code ainda não está disponível
        if isinstance(result, dict) and result.get('count') == 0:
            if retry:
                # Aguardar um pouco e tentar novamente
                logger.info(f"QR code ainda não disponível para {instance_id}, aguardando...")
                time.sleep(3)
                return self.get_qr(instance_id, retry=False)
            else:
                return {
                    'success': False,
                    'error': 'QR code ainda não disponível. Aguarde alguns segundos e tente novamente.',
                    'status': 'waiting'
                }
        
        # Tentar endpoint alternativo
        endpoint_alt = f'/instance/qrcode/{instance_id}'
        result_alt = self._request('GET', endpoint_alt, raise_on_error=False)
        
        qrcode_data_alt = self._extract_qrcode_from_response(result_alt)
        if qrcode_data_alt:
            return {
                'success': True,
                'qrcode': qrcode_data_alt.get('qrcode'),
                'qrcode_url': qrcode_data_alt.get('qrcode_url'),
            }
        
        # Se não encontrou QR code em nenhum formato
        return {
            'success': False,
            'error': 'QR code não encontrado. Verifique se a instância foi criada corretamente.',
            'raw_response': result
        }
    
    def _extract_qrcode_from_response(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extrai QR code de diferentes formatos de resposta da Evolution API
        
        Args:
            response: Resposta da API
        
        Returns:
            {'qrcode': str, 'qrcode_url': str} ou None
        """
        if not isinstance(response, dict):
            return None
        
        # Formato 1: {"qrcode": {"base64": "...", "code": "..."}}
        if 'qrcode' in response:
            qrcode_data = response.get('qrcode', {})
            if isinstance(qrcode_data, dict):
                qrcode_base64 = (
                    qrcode_data.get('base64') or 
                    qrcode_data.get('qrcode') or 
                    qrcode_data.get('code')
                )
                if qrcode_base64:
                    return {
                        'qrcode': qrcode_base64,
                        'qrcode_url': qrcode_data.get('url'),
                    }
            elif isinstance(qrcode_data, str):
                # QR code pode vir como string direta
                return {
                    'qrcode': qrcode_data,
                    'qrcode_url': None,
                }
        
        # Formato 2: QR code no nível raiz
        if 'base64' in response:
            qrcode_base64 = response.get('base64')
            if qrcode_base64:
                return {
                    'qrcode': qrcode_base64,
                    'qrcode_url': response.get('url'),
                }
        
        # Formato 3: Dentro de "data" (array ou objeto)
        if 'data' in response:
            data = response.get('data')
            if isinstance(data, list) and len(data) > 0:
                qr_data = data[0]
                if isinstance(qr_data, dict):
                    qrcode_base64 = (
                        qr_data.get('base64') or 
                        qr_data.get('qrcode') or 
                        (qr_data.get('qrcode', {}).get('base64') if isinstance(qr_data.get('qrcode'), dict) else None)
                    )
                    if qrcode_base64:
                        return {
                            'qrcode': qrcode_base64,
                            'qrcode_url': qr_data.get('url'),
                        }
            elif isinstance(data, dict):
                qrcode_base64 = (
                    data.get('base64') or 
                    data.get('qrcode') or 
                    (data.get('qrcode', {}).get('base64') if isinstance(data.get('qrcode'), dict) else None)
                )
                if qrcode_base64:
                    return {
                        'qrcode': qrcode_base64,
                        'qrcode_url': data.get('url'),
                    }
        
        # Formato 4: Direto como string no campo "code"
        if 'code' in response:
            code = response.get('code')
            if isinstance(code, str) and len(code) > 100:  # Provavelmente base64
                return {
                    'qrcode': code,
                    'qrcode_url': response.get('url'),
                }
        
        return None
    
    def get_status(self, instance_id: str) -> Dict[str, Any]:
        """
        Obtém status da instância
        
        Args:
            instance_id: ID da instância
        
        Returns:
            {
                'success': bool,
                'status': 'open' | 'close' | 'connecting' | ...,
                'phone_number': '...',
                'phone_name': '...'
            }
        """
        endpoint = f'/instance/fetchInstances'
        result = self._request('GET', endpoint)
        
        # Buscar instância específica na lista
        if result.get('success') and isinstance(result.get('instance'), list):
            for instance in result.get('instance', []):
                if instance.get('instanceName') == instance_id:
                    return {
                        'success': True,
                        'status': instance.get('state', 'unknown'),
                        'phone_number': instance.get('phone', {}).get('number'),
                        'phone_name': instance.get('phone', {}).get('name'),
                    }
        
        return {'success': False, 'error': 'Instância não encontrada'}
    
    def send_text(self, instance_id: str, to: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        
        Args:
            instance_id: ID da instância
            to: Número de destino (formato: 5511999999999 ou +5511999999999)
            text: Texto da mensagem
        
        Returns:
            {
                'success': bool,
                'message_id': '...',
                'error': '...' (se houver)
            }
        """
        # Normalizar número (remover + se houver)
        to = to.replace('+', '')
        
        endpoint = f'/message/sendText/{instance_id}'
        data = {
            'number': to,
            'text': text,
        }
        
        result = self._request('POST', endpoint, data)
        return result
    
    def send_media(self, instance_id: str, to: str, media_url: str, caption: str = '') -> Dict[str, Any]:
        """
        Envia mídia (imagem, vídeo, etc.)
        
        Args:
            instance_id: ID da instância
            to: Número de destino
            media_url: URL da mídia
            caption: Legenda (opcional)
        
        Returns:
            {
                'success': bool,
                'message_id': '...',
                'error': '...' (se houver)
            }
        """
        # Normalizar número
        to = to.replace('+', '')
        
        endpoint = f'/message/sendMedia/{instance_id}'
        data = {
            'number': to,
            'mediaUrl': media_url,
            'caption': caption,
        }
        
        result = self._request('POST', endpoint, data)
        return result
    
    def delete_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Deleta instância
        
        Args:
            instance_id: ID da instância
        
        Returns:
            {
                'success': bool,
                'error': '...' (se houver)
            }
        """
        endpoint = f'/instance/delete/{instance_id}'
        result = self._request('DELETE', endpoint)
        return result
    
    def restart_instance(self, instance_id: str) -> Dict[str, Any]:
        """
        Reinicia instância
        
        Args:
            instance_id: ID da instância
        
        Returns:
            {
                'success': bool,
                'error': '...' (se houver)
            }
        """
        endpoint = f'/instance/restart/{instance_id}'
        result = self._request('PUT', endpoint)
        return result


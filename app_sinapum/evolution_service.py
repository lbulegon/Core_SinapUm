"""
Serviço para integração com Evolution API (WhatsApp)
"""
import requests
import logging
from django.conf import settings
import time

logger = logging.getLogger(__name__)

# Configurações da Evolution API
EVOLUTION_API_URL = getattr(settings, 'EVOLUTION_API_URL', 'http://127.0.0.1:8004')
EVOLUTION_API_KEY = getattr(settings, 'EVOLUTION_API_KEY', 'GKvy6psn-8HHpBQ4HAHKFOXnwjHR-oSzeGZzCaws0xg')
EVOLUTION_INSTANCE_NAME = getattr(settings, 'EVOLUTION_INSTANCE_NAME', 'core_sinapum')


class EvolutionAPIService:
    """Classe para interagir com a Evolution API"""
    
    def __init__(self):
        self.base_url = EVOLUTION_API_URL.rstrip('/')
        self.api_key = EVOLUTION_API_KEY
        self.instance_name = EVOLUTION_INSTANCE_NAME
        self.headers = {
            'apikey': self.api_key,
            'Content-Type': 'application/json'
        }
    
    def create_instance(self, instance_name=None):
        """
        Cria uma nova instância WhatsApp na Evolution API
        
        Args:
            instance_name: Nome da instância (opcional, usa padrão se None)
        
        Returns:
            dict: Resposta da API com informações da instância criada
        """
        if instance_name is None:
            instance_name = EVOLUTION_INSTANCE_NAME
        
        url = f"{self.base_url}/instance/create"
        payload = {
            "instanceName": instance_name,
            "token": self.api_key,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS"
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=15)
            
            # Log detalhado em caso de erro
            if response.status_code != 201:
                logger.error(f"Erro ao criar instância: Status {response.status_code}, Response: {response.text[:200]}")
                return {
                    'success': False,
                    'error': f"Erro {response.status_code}: {response.text[:200]}",
                    'instance_name': instance_name
                }
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"Instância '{instance_name}' criada com sucesso")
            return {
                'success': True,
                'data': result,
                'instance_name': instance_name
            }
        except requests.exceptions.Timeout:
            logger.error(f"Timeout ao criar instância '{instance_name}'")
            return {
                'success': False,
                'error': 'Timeout ao criar instância. Tente novamente.',
                'instance_name': instance_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao criar instância: {e}")
            return {
                'success': False,
                'error': str(e),
                'instance_name': instance_name
            }
    
    def get_qrcode(self, instance_name=None):
        """
        Obtém o QR code para conexão do WhatsApp
        
        Args:
            instance_name: Nome da instância (opcional, usa padrão se None)
        
        Returns:
            dict: Resposta com base64 do QR code ou status da conexão
        """
        if instance_name is None:
            instance_name = EVOLUTION_INSTANCE_NAME
        
        # Primeiro verificar o status da instância
        status_result = self.get_instance_status(instance_name)
        if status_result.get('success'):
            if status_result.get('status') == 'open':
                return {
                    'success': True,
                    'connected': True,
                    'instance_name': instance_name,
                    'status': 'connected',
                    'profile_name': status_result.get('profile_name'),
                    'number': status_result.get('number')
                }
        
        # Na Evolution API v2.1.1, o QR code vem através do endpoint /instance/connect
        # NOTA: Este endpoint retorna {"count": 0} quando o QR code ainda não está disponível
        # O QR code geralmente é obtido via WebSocket, mas vamos tentar via REST primeiro
        url = f"{self.base_url}/instance/connect/{instance_name}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            logger.debug(f"Response status: {response.status_code}, Response: {response.text[:500]}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Log para debug
                logger.debug(f"QR code response: {result}")
                
                # Verificar diferentes formatos de resposta
                # Formato 1: {"qrcode": {"base64": "...", "code": "..."}}
                if isinstance(result, dict) and 'qrcode' in result:
                    qrcode_data = result.get('qrcode', {})
                    if isinstance(qrcode_data, dict):
                        # Pode ser base64 diretamente ou dentro de um objeto
                        qrcode_base64 = qrcode_data.get('base64') or qrcode_data.get('qrcode') or qrcode_data.get('code')
                        if qrcode_base64:
                            return {
                                'success': True,
                                'qrcode': qrcode_base64,
                                'qrcode_base64': qrcode_base64,
                                'base64': qrcode_base64,
                                'instance_name': instance_name,
                                'status': 'qrcode'
                            }
                
                # Formato 2: QR code pode estar no nível raiz
                if isinstance(result, dict) and 'base64' in result:
                    qrcode_base64 = result.get('base64')
                    if qrcode_base64:
                        return {
                            'success': True,
                            'qrcode': qrcode_base64,
                            'qrcode_base64': qrcode_base64,
                            'base64': qrcode_base64,
                            'instance_name': instance_name,
                            'status': 'qrcode'
                        }
                
                # Formato 3: Pode ter um array de QR codes
                if isinstance(result, dict) and 'data' in result:
                    data = result.get('data', [])
                    if isinstance(data, list) and len(data) > 0:
                        qr_data = data[0]
                        if isinstance(qr_data, dict):
                            qrcode_base64 = qr_data.get('base64') or qr_data.get('qrcode') or (qr_data.get('qrcode', {}).get('base64') if isinstance(qr_data.get('qrcode'), dict) else None)
                            if qrcode_base64:
                                return {
                                    'success': True,
                                    'qrcode': qrcode_base64,
                                    'qrcode_base64': qrcode_base64,
                                    'base64': qrcode_base64,
                                    'instance_name': instance_name,
                                    'status': 'qrcode'
                                }
                
                # Se retornou {"count": 0}, significa que o QR code ainda não está disponível
                if isinstance(result, dict) and result.get('count') == 0:
                    logger.info(f"QR code ainda não disponível para instância {instance_name}")
                    return {
                        'success': True,
                        'qrcode': None,
                        'instance_name': instance_name,
                        'status': 'waiting',
                        'message': 'Aguardando geração do QR code. Tente novamente em alguns segundos.'
                    }
            
            # Se não encontrou QR code, a instância pode estar aguardando conexão
            # Retornar status indicando que precisa aguardar
            logger.warning(f"QR code não encontrado na resposta. Status: {response.status_code}, Response: {response.text[:200]}")
            return {
                'success': True,
                'qrcode': None,
                'instance_name': instance_name,
                'status': 'waiting',
                'message': 'Aguardando geração do QR code. Tente novamente em alguns segundos.'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter QR code: {e}")
            return {
                'success': False,
                'error': str(e),
                'instance_name': instance_name
            }
    
    def get_instance_status(self, instance_name=None):
        """
        Obtém o status da instância WhatsApp
        
        Args:
            instance_name: Nome da instância (opcional, usa padrão se None)
        
        Returns:
            dict: Status da instância (open, close, connecting, etc)
        """
        if instance_name is None:
            instance_name = EVOLUTION_INSTANCE_NAME
        
        url = f"{self.base_url}/instance/fetchInstances"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            instances = response.json()
            
            # Buscar a instância específica
            for instance in instances:
                if instance.get('name') == instance_name:
                    return {
                        'success': True,
                        'instance_name': instance_name,
                        'status': instance.get('connectionStatus', 'close'),
                        'owner_jid': instance.get('ownerJid'),
                        'profile_name': instance.get('profileName'),
                        'number': instance.get('number'),
                        'data': instance
                    }
            
            return {
                'success': False,
                'error': f'Instância "{instance_name}" não encontrada',
                'instance_name': instance_name
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao obter status da instância: {e}")
            return {
                'success': False,
                'error': str(e),
                'instance_name': instance_name
            }
    
    def fetch_instances(self):
        """
        Lista todas as instâncias disponíveis
        
        Returns:
            dict: Lista de instâncias
        """
        url = f"{self.base_url}/instance/fetchInstances"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            instances = response.json()
            return {
                'success': True,
                'instances': instances
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao listar instâncias: {e}")
            return {
                'success': False,
                'error': str(e),
                'instances': []
            }
    
    def delete_instance(self, instance_name=None):
        """
        Deleta uma instância WhatsApp
        
        Args:
            instance_name: Nome da instância (opcional, usa padrão se None)
        
        Returns:
            dict: Resultado da deleção
        """
        if instance_name is None:
            instance_name = EVOLUTION_INSTANCE_NAME
        
        url = f"{self.base_url}/instance/delete/{instance_name}"
        
        try:
            response = requests.delete(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info(f"Instância '{instance_name}' deletada com sucesso")
            return {
                'success': True,
                'instance_name': instance_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao deletar instância: {e}")
            return {
                'success': False,
                'error': str(e),
                'instance_name': instance_name
            }
    
    def restart_instance(self, instance_name=None):
        """
        Reinicia uma instância WhatsApp
        
        Args:
            instance_name: Nome da instância (opcional, usa padrão se None)
        
        Returns:
            dict: Resultado do restart
        """
        if instance_name is None:
            instance_name = EVOLUTION_INSTANCE_NAME
        
        url = f"{self.base_url}/instance/restart/{instance_name}"
        
        try:
            response = requests.put(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            logger.info(f"Instância '{instance_name}' reiniciada com sucesso")
            return {
                'success': True,
                'instance_name': instance_name
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao reiniciar instância: {e}")
            return {
                'success': False,
                'error': str(e),
                'instance_name': instance_name
            }


# Função helper para uso fácil
def get_evolution_service():
    """Retorna uma instância do EvolutionAPIService"""
    return EvolutionAPIService()


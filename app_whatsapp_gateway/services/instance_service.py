# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway.services.instance_service
# ============================================================================

import logging
from typing import Dict, Any, Optional
from django.utils import timezone
from ..models import EvolutionInstance
from ..clients import EvolutionClient
from .websocket_service import websocket_service

logger = logging.getLogger(__name__)


class InstanceService:
    """
    Service para gerenciar instâncias Evolution - Multi-tenant
    """
    
    def __init__(self):
        self.evolution_client = EvolutionClient()
    
    def get_or_create_instance(self, shopper_id: str, instance_id: Optional[str] = None) -> tuple[EvolutionInstance, bool]:
        """
        Obtém ou cria instância Evolution para um shopper
        
        Args:
            shopper_id: ID do Shopper
            instance_id: ID da instância (opcional, usa shopper_id se não fornecido)
        
        Returns:
            (EvolutionInstance, created)
        """
        if not instance_id:
            instance_id = f"shopper_{shopper_id}"
        
        instance, created = EvolutionInstance.objects.get_or_create(
            shopper_id=shopper_id,
            instance_id=instance_id,
            defaults={
                'status': EvolutionInstance.InstanceStatus.CREATING,
            }
        )
        
        return instance, created
    
    def create_instance(self, shopper_id: str, instance_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Cria nova instância na Evolution API
        
        Args:
            shopper_id: ID do Shopper
            instance_id: ID da instância (opcional)
        
        Returns:
            {
                'success': bool,
                'instance': EvolutionInstance,
                'qrcode': str (base64),
                'error': str (se houver)
            }
        """
        if not instance_id:
            instance_id = f"shopper_{shopper_id}"
        
        # Criar no banco
        instance, created = self.get_or_create_instance(shopper_id, instance_id)
        
        if not created and instance.status == EvolutionInstance.InstanceStatus.OPEN:
            # Instância já existe e está conectada
            return {
                'success': True,
                'instance': instance,
                'qrcode': instance.qrcode,
                'message': 'Instância já existe e está conectada'
            }
        
        # Criar na Evolution API
        result = self.evolution_client.create_instance(instance_id, qrcode=True)
        
        # Verificar se a criação foi bem-sucedida
        # A Evolution API pode retornar sucesso mesmo sem QR code imediato
        creation_success = (
            result.get('success') or 
            (not result.get('error') and (result.get('instance') or result.get('instanceName')))
        )
        
        if creation_success:
            # Atualizar instância no banco
            instance.status = EvolutionInstance.InstanceStatus.CONNECTING
            
            # Tentar obter QR code se não veio na resposta
            if 'qrcode' in result and result.get('qrcode'):
                instance.qrcode = result.get('qrcode')
                instance.qrcode_url = result.get('qrcode_url')
            else:
                # QR code não veio na criação, tentar obter agora
                logger.info(f"QR code não veio na criação, tentando obter para {instance_id}")
                qr_result = self.evolution_client.get_qr(instance_id, retry=True)
                if qr_result.get('success') and qr_result.get('qrcode'):
                    instance.qrcode = qr_result.get('qrcode')
                    instance.qrcode_url = qr_result.get('qrcode_url')
                else:
                    logger.warning(f"QR code ainda não disponível para {instance_id}: {qr_result.get('error')}")
            
            instance.save()
            
            # Iniciar WebSocket listener para receber eventos de QR code em tempo real
            try:
                websocket_service.start_listening_for_instance(instance_id)
                logger.info(f"WebSocket listener iniciado para {instance_id}")
            except Exception as e:
                logger.warning(f"Erro ao iniciar WebSocket listener (não crítico): {e}")
            
            return {
                'success': True,
                'instance': instance,
                'qrcode': instance.qrcode,
                'qrcode_url': instance.qrcode_url,
                'message': 'Instância criada. QR code pode estar sendo gerado.' if not instance.qrcode else None
            }
        else:
            instance.status = EvolutionInstance.InstanceStatus.UNKNOWN
            instance.save()
            return {
                'success': False,
                'instance': instance,
                'error': result.get('error', 'Erro desconhecido ao criar instância')
            }
    
    def get_qr(self, instance_id: str, shopper_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém QR Code da instância
        
        Args:
            instance_id: ID da instância
            shopper_id: ID do Shopper (opcional, para validação)
        
        Returns:
            {
                'success': bool,
                'qrcode': str (base64),
                'qrcode_url': str,
                'error': str (se houver)
            }
        """
        try:
            instance = EvolutionInstance.objects.get(instance_id=instance_id)
            
            # Validar shopper_id se fornecido
            if shopper_id and instance.shopper_id != shopper_id:
                return {
                    'success': False,
                    'error': 'Instância não pertence a este shopper'
                }
            
            # Se já tem QR code e está conectando, retornar do banco
            if instance.qrcode and instance.status == EvolutionInstance.InstanceStatus.CONNECTING:
                return {
                    'success': True,
                    'qrcode': instance.qrcode,
                    'qrcode_url': instance.qrcode_url,
                }
            
            # Buscar novo QR code da Evolution API
            result = self.evolution_client.get_qr(instance_id, retry=True)
            
            if result.get('success') and result.get('qrcode'):
                # Atualizar no banco
                instance.qrcode = result.get('qrcode')
                instance.qrcode_url = result.get('qrcode_url')
                instance.status = EvolutionInstance.InstanceStatus.CONNECTING
                instance.save()
                
                return {
                    'success': True,
                    'qrcode': instance.qrcode,
                    'qrcode_url': instance.qrcode_url,
                }
            else:
                # QR code ainda não disponível, mas não é erro fatal
                error_msg = result.get('error', 'QR code ainda não disponível')
                status = result.get('status', 'waiting')
                
                if status == 'waiting':
                    # QR code está sendo gerado, retornar sucesso mas sem QR code ainda
                    return {
                        'success': True,
                        'qrcode': None,
                        'qrcode_url': None,
                        'status': 'waiting',
                        'message': error_msg
                    }
                else:
                    return {
                        'success': False,
                        'error': error_msg
                    }
                
        except EvolutionInstance.DoesNotExist:
            return {
                'success': False,
                'error': 'Instância não encontrada'
            }
    
    def update_status(self, instance_id: str, status: str, phone_number: Optional[str] = None, phone_name: Optional[str] = None) -> bool:
        """
        Atualiza status da instância
        
        Args:
            instance_id: ID da instância
            status: Novo status
            phone_number: Número do WhatsApp (opcional)
            phone_name: Nome do WhatsApp (opcional)
        
        Returns:
            True se atualizado com sucesso
        """
        try:
            instance = EvolutionInstance.objects.get(instance_id=instance_id)
            
            # Mapear status
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
            
            return True
            
        except EvolutionInstance.DoesNotExist:
            logger.warning(f"Instância {instance_id} não encontrada para atualizar status")
            return False


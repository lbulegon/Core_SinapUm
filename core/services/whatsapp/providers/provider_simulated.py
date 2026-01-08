"""
Provider Simulated - Simula envio e grava localmente
=====================================================

Provider para desenvolvimento e testes que simula envio
e grava mensagens em uma tabela/log local.
"""
import logging
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from django.apps import apps
from django.utils import timezone
from ..interfaces import IWhatsAppProvider
from ..schemas import ProviderResult, ProviderHealth

logger = logging.getLogger(__name__)


def get_simulated_message_model():
    """
    Obtém modelo SimulatedMessage dinamicamente
    
    Model definido em models.py para migrations.
    Importado dinamicamente aqui para evitar circular imports.
    """
    try:
        return apps.get_model('core.services.whatsapp', 'SimulatedMessage')
    except LookupError:
        # Se app não está instalado, retornar None
        return None


class ProviderSimulated(IWhatsAppProvider):
    """
    Provider que simula envio e grava localmente
    
    Útil para:
    - Desenvolvimento local
    - Testes automatizados
    - Demonstrações
    """
    
    @property
    def name(self) -> str:
        return "simulated"
    
    def send_text(
        self,
        to: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Simula envio de texto e grava localmente"""
        try:
            # Obter modelo dinamicamente
            SimulatedMessage = get_simulated_message_model()
            if not SimulatedMessage:
                # Se modelo não está disponível, apenas logar
                logger.warning("SimulatedMessage model não disponível, apenas logando")
                return ProviderResult(
                    provider_name=self.name,
                    status="sent",
                    message_id=f"sim_{uuid.uuid4()}",
                    metadata={'logged_only': True, **(metadata or {})}
                )
            
            # Normalizar número
            to_normalized = self._normalize_phone(to)
            
            # Gravar mensagem simulada
            message = SimulatedMessage.objects.create(
                to=to_normalized,
                text=text,
                message_type='text',
                metadata=metadata or {}
            )
            
            logger.info(
                f"[WhatsApp Simulated] Mensagem simulada gravada",
                extra={
                    'message_id': str(message.id),
                    'to': to_normalized,
                    'text_length': len(text),
                    'metadata': metadata or {}
                }
            )
            
            return ProviderResult(
                provider_name=self.name,
                status="sent",
                message_id=str(message.id),
                metadata={
                    'simulated': True,
                    'saved_at': message.created_at.isoformat(),
                    **({} if metadata is None else metadata)
                }
            )
        except Exception as e:
            logger.error(f"Erro ao simular mensagem: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
    
    def send_media(
        self,
        to: str,
        media_url: str,
        caption: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ProviderResult:
        """Simula envio de mídia e grava localmente"""
        try:
            # Obter modelo dinamicamente
            SimulatedMessage = get_simulated_message_model()
            if not SimulatedMessage:
                # Se modelo não está disponível, apenas logar
                logger.warning("SimulatedMessage model não disponível, apenas logando")
                return ProviderResult(
                    provider_name=self.name,
                    status="sent",
                    message_id=f"sim_{uuid.uuid4()}",
                    metadata={'logged_only': True, **(metadata or {})}
                )
            
            # Normalizar número
            to_normalized = self._normalize_phone(to)
            
            # Gravar mensagem simulada
            message = SimulatedMessage.objects.create(
                to=to_normalized,
                media_url=media_url,
                caption=caption or '',
                message_type='media',
                metadata=metadata or {}
            )
            
            logger.info(
                f"[WhatsApp Simulated] Mídia simulada gravada",
                extra={
                    'message_id': str(message.id),
                    'to': to_normalized,
                    'media_url': media_url,
                    'metadata': metadata or {}
                }
            )
            
            return ProviderResult(
                provider_name=self.name,
                status="sent",
                message_id=str(message.id),
                metadata={
                    'simulated': True,
                    'saved_at': message.created_at.isoformat(),
                    **({} if metadata is None else metadata)
                }
            )
        except Exception as e:
            logger.error(f"Erro ao simular mídia: {e}", exc_info=True)
            return ProviderResult(
                provider_name=self.name,
                status="failed",
                error=str(e),
                metadata=metadata or {}
            )
    
    def healthcheck(self) -> ProviderHealth:
        """Verifica saúde (sempre saudável se DB disponível)"""
        try:
            # Obter modelo dinamicamente
            SimulatedMessage = get_simulated_message_model()
            if not SimulatedMessage:
                # Se modelo não está disponível, ainda é saudável (apenas não grava)
                return ProviderHealth(
                    provider_name=self.name,
                    status="healthy",
                    message="Simulated provider is healthy (logging only)",
                    last_check=datetime.now()
                )
            
            # Testar acesso ao banco
            SimulatedMessage.objects.count()
            return ProviderHealth(
                provider_name=self.name,
                status="healthy",
                message="Simulated provider is healthy",
                last_check=datetime.now()
            )
        except Exception as e:
            return ProviderHealth(
                provider_name=self.name,
                status="unhealthy",
                message=f"Database error: {str(e)}",
                last_check=datetime.now()
            )
    
    @staticmethod
    def _normalize_phone(phone: str) -> str:
        """Normaliza número de telefone"""
        # Remove caracteres especiais
        phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        # Garante que começa com +
        if not phone.startswith("+"):
            if phone.startswith("55"):
                phone = f"+{phone}"
            else:
                # Assumir número brasileiro sem código do país
                phone = f"+55{phone}"
        
        return phone

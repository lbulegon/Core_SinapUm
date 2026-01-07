# ============================================================================
# ETAPA 5 - Resposta Automática Fora do Horário
# AutoReplyService: Detecção e envio de mensagens fora do horário
# ============================================================================

from typing import Dict, Any, Optional
from datetime import datetime, time
import logging

logger = logging.getLogger(__name__)


class AutoReplyService:
    """
    Serviço para resposta automática fora do horário de atendimento.
    
    Funcionalidades:
    - Detecta mensagens fora do horário configurado
    - Envia mensagem contextual com link do catálogo
    - Nunca inicia negociação automática
    
    REGRA: IA apenas envia mensagem informativa, nunca negocia.
    """
    
    def __init__(self):
        self.logger = logger
    
    def is_business_hours(
        self,
        shopper_config: Dict[str, Any],
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Verifica se está dentro do horário de atendimento.
        
        Args:
            shopper_config: Configuração do shopper com horários
            current_time: Hora atual (opcional, usa datetime.now() se None)
        
        Returns:
            True se está dentro do horário, False caso contrário
        """
        if not shopper_config.get('horario_atendimento_habilitado'):
            # Se não está habilitado, considera sempre dentro do horário
            return True
        
        if current_time is None:
            current_time = datetime.now()
        
        current_weekday = current_time.weekday()  # 0=Segunda, 6=Domingo
        current_time_only = current_time.time()
        
        # Verificar se o dia atual está nos dias de atendimento
        dias_atendimento = shopper_config.get('dias_atendimento', [])
        if dias_atendimento and current_weekday not in dias_atendimento:
            return False
        
        # Verificar se está dentro do horário
        inicio = shopper_config.get('horario_atendimento_inicio')
        fim = shopper_config.get('horario_atendimento_fim')
        
        if inicio and fim:
            if isinstance(inicio, str):
                inicio = datetime.strptime(inicio, '%H:%M:%S').time()
            if isinstance(fim, str):
                fim = datetime.strptime(fim, '%H:%M:%S').time()
            
            if inicio <= fim:
                # Horário normal (ex: 09:00 - 18:00)
                return inicio <= current_time_only <= fim
            else:
                # Horário que cruza meia-noite (ex: 22:00 - 02:00)
                return current_time_only >= inicio or current_time_only <= fim
        
        # Se não há horário configurado, considera dentro do horário
        return True
    
    def generate_auto_reply_message(
        self,
        shopper_config: Dict[str, Any],
        catalog_url: Optional[str] = None
    ) -> str:
        """
        Gera mensagem automática para fora do horário.
        
        Args:
            shopper_config: Configuração do shopper
            catalog_url: URL do catálogo (opcional)
        
        Returns:
            Mensagem a ser enviada
        """
        mensagem_personalizada = shopper_config.get('mensagem_fora_horario', '').strip()
        
        if mensagem_personalizada:
            # Usar mensagem personalizada do shopper
            message = mensagem_personalizada
        else:
            # Mensagem padrão
            message = (
                "Olá! Recebi sua mensagem, mas no momento estou fora do horário de atendimento. "
                "Vou responder assim que possível!"
            )
        
        # Adicionar link do catálogo se disponível
        if catalog_url:
            message += f"\n\nEnquanto isso, você pode conferir meus produtos: {catalog_url}"
        
        return message
    
    def should_send_auto_reply(
        self,
        shopper_config: Dict[str, Any],
        last_message_time: Optional[datetime] = None
    ) -> bool:
        """
        Verifica se deve enviar resposta automática.
        
        Args:
            shopper_config: Configuração do shopper
            last_message_time: Hora da última mensagem recebida
        
        Returns:
            True se deve enviar resposta automática
        """
        if not shopper_config.get('horario_atendimento_habilitado'):
            return False
        
        if last_message_time is None:
            last_message_time = datetime.now()
        
        # Verificar se a mensagem foi recebida fora do horário
        return not self.is_business_hours(shopper_config, last_message_time)
    
    def get_catalog_url(self, shopper_config: Dict[str, Any]) -> Optional[str]:
        """
        Gera URL do catálogo do shopper.
        
        Args:
            shopper_config: Configuração do shopper
        
        Returns:
            URL do catálogo ou None
        """
        subdominio = shopper_config.get('catalogo_subdominio')
        dominio_proprio = shopper_config.get('catalogo_dominio_proprio')
        
        if dominio_proprio:
            return f"https://{dominio_proprio}"
        elif subdominio:
            # TODO: Obter URL base das configurações
            base_url = "https://vitrinezap.com.br"  # Placeholder
            return f"{base_url}/catalogo/{subdominio}/"
        
        return None


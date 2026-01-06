"""
Adapter para WhatsApp - gera payloads prontos para cada canal
"""
import logging
from typing import Dict, Any, List
from services.creative_engine_service.contracts import CreativeVariant, CreativeContext

logger = logging.getLogger(__name__)


class WhatsAppAdapter:
    """Adapter para formatar criativos para WhatsApp"""
    
    def adapt(
        self,
        variant: CreativeVariant,
        context: CreativeContext
    ) -> Dict[str, Any]:
        """
        Adapta variante para canal específico do WhatsApp
        
        Args:
            variant: Variante do criativo
            context: Contexto de adaptação
        
        Returns:
            Payload pronto para o canal
        """
        channel = context.channel
        
        if channel == "status":
            return self._adapt_for_status(variant, context)
        elif channel == "group":
            return self._adapt_for_group(variant, context)
        elif channel == "private":
            return self._adapt_for_private(variant, context)
        else:
            logger.warning(f"Canal desconhecido: {channel}, usando formato genérico")
            return self._adapt_generic(variant, context)
    
    def _adapt_for_status(self, variant: CreativeVariant, context: CreativeContext) -> Dict[str, Any]:
        """Adapta para WhatsApp Status (<= 250 chars)"""
        return {
            "channel": "status",
            "image_url": variant.image_url,
            "text": variant.text_short or variant.text_medium or "",
            "cta": variant.ctas[0] if variant.ctas else "Saiba mais",
            "max_length": 250,
        }
    
    def _adapt_for_group(self, variant: CreativeVariant, context: CreativeContext) -> Dict[str, Any]:
        """Adapta para WhatsApp Grupo (texto médio + 1 variação de CTA)"""
        return {
            "channel": "group",
            "image_url": variant.image_url,
            "text": variant.text_medium or variant.text_long or "",
            "cta_primary": variant.ctas[0] if variant.ctas else "Saiba mais",
            "cta_secondary": variant.ctas[1] if len(variant.ctas) > 1 else None,
            "max_length": 500,
        }
    
    def _adapt_for_private(self, variant: CreativeVariant, context: CreativeContext) -> Dict[str, Any]:
        """Adapta para WhatsApp 1:1 (texto longo + roteiro de 2 mensagens)"""
        discourse = variant.discourse or {}
        
        # Mensagem inicial
        message_1 = {
            "text": variant.text_long or variant.text_medium or "",
            "image_url": variant.image_url,
        }
        
        # Mensagem de follow-up (se silêncio)
        message_2 = {
            "text": self._generate_followup(discourse, context),
            "delay_seconds": 300,  # 5 minutos
        }
        
        return {
            "channel": "private",
            "messages": [
                message_1,
                message_2,
            ],
            "discourse": discourse,
            "cta": variant.ctas[0] if variant.ctas else "Quer saber mais?",
        }
    
    def _generate_followup(self, discourse: Dict[str, Any], context: CreativeContext) -> str:
        """Gera mensagem de follow-up"""
        opening = discourse.get("opening", "")
        if opening:
            return f"{opening} Ainda tem interesse?"
        return "Ainda tem interesse? Posso ajudar com mais informações!"
    
    def _adapt_generic(self, variant: CreativeVariant, context: CreativeContext) -> Dict[str, Any]:
        """Adaptação genérica"""
        return {
            "channel": context.channel,
            "image_url": variant.image_url,
            "text_short": variant.text_short,
            "text_medium": variant.text_medium,
            "text_long": variant.text_long,
            "ctas": variant.ctas,
        }

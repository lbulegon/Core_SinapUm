"""
Adapter genérico - permite reutilização fora do WhatsApp
"""
import logging
from typing import Dict, Any
from services.creative_engine_service.contracts import CreativeVariant, CreativeContext

logger = logging.getLogger(__name__)


class GenericAdapter:
    """Adapter genérico para qualquer canal"""
    
    def adapt(
        self,
        variant: CreativeVariant,
        context: CreativeContext
    ) -> Dict[str, Any]:
        """
        Adapta variante para formato genérico
        
        Args:
            variant: Variante do criativo
            context: Contexto de adaptação
        
        Returns:
            Payload genérico
        """
        return {
            "variant_id": variant.variant_id,
            "strategy": variant.strategy,
            "channel": context.channel,
            "locale": context.locale,
            "tone": context.tone,
            "image_url": variant.image_url,
            "text_short": variant.text_short,
            "text_medium": variant.text_medium,
            "text_long": variant.text_long,
            "discourse": variant.discourse,
            "ctas": variant.ctas,
            "metadata": {
                "time_of_day": context.time_of_day,
                "stock_level": context.stock_level,
                "price_sensitivity": context.price_sensitivity,
                "campaign_tag": context.campaign_tag,
            }
        }

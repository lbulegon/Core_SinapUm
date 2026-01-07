# ============================================================================
# ETAPA 3 - Ferramentas de Marketing
# MarketingEventService: Disparo de eventos de marketing
# ============================================================================

from typing import Dict, Any, Optional
import logging
from .tracking import TrackingService

logger = logging.getLogger(__name__)


class MarketingEventService:
    """
    Serviço para disparo de eventos de marketing.
    
    Eventos suportados:
    - product_view: Cliente visualizou produto
    - add_to_cart: Produto adicionado ao carrinho
    - checkout_intent: Cliente iniciou checkout
    
    REGRA: Eventos são opcionais e não afetam o fluxo principal.
    """
    
    def __init__(self):
        self.tracking_service = TrackingService()
        self.logger = logger
    
    def track_product_view(
        self,
        shopper_id: str,
        product_id: str,
        customer_id: Optional[str] = None
    ) -> None:
        """
        Dispara evento de visualização de produto.
        
        Args:
            shopper_id: ID do Shopper
            product_id: ID do produto
            customer_id: ID do cliente (opcional)
        """
        self.tracking_service.track_event(
            event_name='product_view',
            shopper_id=shopper_id,
            customer_id=customer_id,
            product_id=product_id,
            data={
                'event_type': 'product_view',
                'timestamp': None  # Será preenchido pelo tracking_service
            }
        )
    
    def track_add_to_cart(
        self,
        shopper_id: str,
        product_id: str,
        quantity: int = 1,
        customer_id: Optional[str] = None,
        variation_id: Optional[str] = None
    ) -> None:
        """
        Dispara evento de adição ao carrinho.
        
        Args:
            shopper_id: ID do Shopper
            product_id: ID do produto
            quantity: Quantidade adicionada
            customer_id: ID do cliente (opcional)
            variation_id: ID da variação (opcional - ETAPA 2)
        """
        self.tracking_service.track_event(
            event_name='add_to_cart',
            shopper_id=shopper_id,
            customer_id=customer_id,
            product_id=product_id,
            data={
                'event_type': 'add_to_cart',
                'quantity': quantity,
                'variation_id': variation_id,
                'timestamp': None
            }
        )
    
    def track_checkout_intent(
        self,
        shopper_id: str,
        customer_id: str,
        cart_total: float,
        product_count: int = 0
    ) -> None:
        """
        Dispara evento de intenção de checkout.
        
        Args:
            shopper_id: ID do Shopper
            customer_id: ID do cliente
            cart_total: Total do carrinho
            product_count: Quantidade de produtos no carrinho
        """
        self.tracking_service.track_event(
            event_name='checkout_intent',
            shopper_id=shopper_id,
            customer_id=customer_id,
            data={
                'event_type': 'checkout_intent',
                'cart_total': cart_total,
                'product_count': product_count,
                'timestamp': None
            }
        )


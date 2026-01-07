# ============================================================================
# ETAPA 3 - Ferramentas de Marketing
# marketing_tools_service
# ============================================================================
# 
# Serviço isolado para ferramentas de marketing, sem contaminar o Core.
# Funcionalidades:
# - Cupons de desconto (associáveis a Shopper, Produto, Campanha)
# - Rastreamento (meta_pixel, google_analytics)
# - Eventos de marketing (product_view, add_to_cart, checkout_intent)
# ============================================================================

from .coupons import CouponService
from .tracking import TrackingService
from .events import MarketingEventService
from .auto_reply import AutoReplyService

__all__ = [
    'CouponService',
    'TrackingService',
    'MarketingEventService',
    'AutoReplyService',
]


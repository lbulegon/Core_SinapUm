# ============================================================================
# ARQUITETURA NOVA - app_whatsapp_gateway
# ============================================================================
# Este app faz parte da NOVA arquitetura multi-tenant.
# 
# ANTIGO (não usar): app_whatsapp_integration (Évora)
# NOVO (usar): app_whatsapp_gateway (Core)
#
# Diferenças:
# - Multi-tenant por shopper_id (vs instância única no antigo)
# - Normalização de eventos em Evento Canônico
# - Integração preparada para OpenMind
# ============================================================================


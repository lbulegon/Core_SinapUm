# ============================================================================
# ARQUITETURA NOVA - app_conversations
# ============================================================================
# Este app faz parte da NOVA arquitetura multi-tenant.
# 
# ANTIGO (não usar): EvolutionMessage, WhatsAppMessageLog (Évora)
# NOVO (usar): Conversation, Message, Suggestion (Core)
#
# Diferenças:
# - Normalização de conversas (não apenas mensagens)
# - Suporte a sugestões de IA
# - Multi-tenant por shopper_id
# - Estado de conversa (assistido/auto)
# ============================================================================


"""Serviço de roteamento de conversa"""
from app.schemas.routing import RouteRequest, RouteResponse
from app.schemas.intent import IntentType


class RoutingService:
    """Roteia conversa entre grupo, privado e humano"""
    
    def route(self, request: RouteRequest) -> RouteResponse:
        """Decide próximo passo da conversa"""
        intent = request.intent_payload.intent
        confidence = request.intent_payload.confidence
        urgency = request.intent_payload.urgency
        
        # Regra 1: buy_now com alta confiança → privado
        if intent == IntentType.BUY_NOW and confidence >= 0.75:
            return RouteResponse(
                next_step="private_chat",
                confidence=confidence,
                reasoning=f"Intent {intent.value} com confiança alta ({confidence:.2f}) - direcionar para chat privado",
                suggested_message="Vamos conversar no privado para fechar seu pedido? 👉"
            )
        
        # Regra 2: urgent → privado
        if urgency >= 0.7:
            return RouteResponse(
                next_step="private_chat",
                confidence=urgency,
                reasoning=f"Urgência alta ({urgency:.2f}) - direcionar para chat privado",
                suggested_message="Vamos conversar no privado para resolver mais rápido? 🚀"
            )
        
        # Regra 3: compare → hint no grupo + convite privado
        if intent == IntentType.COMPARE:
            return RouteResponse(
                next_step="group_hint",
                confidence=confidence,
                reasoning=f"Intent {intent.value} - mostrar comparação no grupo e convidar para privado",
                suggested_message="Vou mostrar algumas opções aqui. Quer comparar melhor no privado? 💬"
            )
        
        # Regra 4: SUPPORT → handoff humano
        if intent == IntentType.SUPPORT:
            return RouteResponse(
                next_step="human_handoff",
                confidence=1.0,
                reasoning=f"Intent {intent.value} requer atendimento humano",
                suggested_message="Vou te conectar com um atendente humano agora 👤"
            )
        
        # Regra 5: objeções complexas ou valor alto → handoff
        # (isso seria verificado no contexto, por enquanto default para group_hint)
        
        # Default: group_hint
        return RouteResponse(
            next_step="group_hint",
            confidence=confidence,
            reasoning=f"Intent {intent.value} - continuar no grupo com dicas",
            suggested_message=None
        )


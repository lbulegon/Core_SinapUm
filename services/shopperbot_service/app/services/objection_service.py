"""Serviço de tratamento de objeções"""
from typing import Dict
from app.schemas.objection import ObjectionRequest, ObjectionResponse
from app.schemas.intent import IntentType


class ObjectionService:
    """Trata objeções do cliente"""
    
    def __init__(self):
        self.objection_patterns = self._build_objection_patterns()
        self.response_templates = self._build_response_templates()
    
    def _build_objection_patterns(self) -> Dict[str, list]:
        """Padrões para detectar tipo de objeção"""
        return {
            "preco": [
                "muito caro", "caro demais", "barato demais", "preço alto",
                "muito caro", "valor alto", "não tenho esse dinheiro",
                "tem mais barato", "quanto custa"
            ],
            "prazo": [
                "demora muito", "quando chega", "prazo de entrega",
                "demora quanto", "entrega rápida", "hoje mesmo"
            ],
            "confianca": [
                "confiável", "garantia", "qualidade", "bom mesmo",
                "recomenda", "vale a pena", "é bom"
            ],
            "comparacao": [
                "melhor que", "diferença", "comparar", "versus",
                "outro lugar", "outra loja", "outro produto"
            ],
            "disponibilidade": [
                "tem certeza", "tem mesmo", "disponível", "tem em estoque",
                "não tem", "esgotou"
            ]
        }
    
    def _build_response_templates(self) -> Dict[str, list]:
        """Templates de resposta por tipo de objeção"""
        return {
            "preco": [
                "Entendo! Posso mostrar opções mais em conta. Temos outras alternativas que podem se encaixar melhor no seu orçamento.",
                "Que tal ver algumas opções com preços mais acessíveis? Posso recomendar produtos similares que cabem no seu bolso.",
            ],
            "prazo": [
                "A entrega é rápida! Normalmente entregamos em X dias. Para retirada, está disponível imediatamente.",
                "Pode retirar hoje mesmo na loja ou escolhemos a entrega mais rápida para você.",
            ],
            "confianca": [
                "Somos uma loja confiável com muitos clientes satisfeitos. Este produto é um dos mais pedidos!",
                "Temos ótimas avaliações e muitos clientes que compram conosco regularmente. Pode confiar!",
            ],
            "comparacao": [
                "Cada produto tem suas vantagens. Vamos comparar os detalhes para você escolher o melhor.",
                "Posso mostrar as diferenças entre as opções para você decidir qual atende melhor suas necessidades.",
            ],
            "disponibilidade": [
                "Sim, está disponível! Pode ter certeza que temos em estoque e pronto para enviar.",
                "Temos sim! Está disponível e pode ser entregue/retirado rapidamente.",
            ]
        }
    
    def respond(self, request: ObjectionRequest) -> ObjectionResponse:
        """Responde a uma objeção"""
        message_lower = request.message.lower()
        
        # Detectar tipo de objeção
        objection_type = self._detect_objection_type(message_lower)
        
        # Gerar resposta
        resposta = self._generate_response(objection_type, request)
        
        # Verificar se precisa handoff
        handoff_required = self._should_handoff(request, objection_type)
        
        # Ações sugeridas
        suggested_actions = self._get_suggested_actions(objection_type)
        
        return ObjectionResponse(
            resposta=resposta,
            handoff_required=handoff_required,
            objection_type=objection_type,
            suggested_actions=suggested_actions
        )
    
    def _detect_objection_type(self, message: str) -> str:
        """Detecta tipo de objeção"""
        scores = {}
        for obj_type, patterns in self.objection_patterns.items():
            score = sum(1 for pattern in patterns if pattern in message)
            if score > 0:
                scores[obj_type] = score
        
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "geral"
    
    def _generate_response(self, objection_type: str, request: ObjectionRequest) -> str:
        """Gera resposta para objeção"""
        templates = self.response_templates.get(objection_type, [
            "Entendo sua preocupação. Como posso ajudar melhor?"
        ])
        
        # Por enquanto, retorna primeiro template (pode ser expandido com seleção inteligente)
        resposta = templates[0]
        
        # Personalizar baseado no contexto
        if request.product_id:
            resposta += f" O produto que você está interessado está disponível."
        
        return resposta
    
    def _should_handoff(self, request: ObjectionRequest, objection_type: str) -> bool:
        """Determina se precisa handoff humano"""
        # Handoff se:
        # - Objeção muito complexa
        # - Múltiplas objeções
        # - Intent é SUPPORT
        if request.intent == IntentType.SUPPORT:
            return True
        
        message_lower = request.message.lower()
        complex_indicators = ["problema", "reclamação", "não funciona", "erro", "cancelar"]
        if any(indicator in message_lower for indicator in complex_indicators):
            return True
        
        return False
    
    def _get_suggested_actions(self, objection_type: str) -> list:
        """Retorna ações sugeridas"""
        actions_map = {
            "preco": ["Ver opções mais baratas", "Negociar preço", "Ver parcelamento"],
            "prazo": ["Ver opções de entrega", "Retirada na loja", "Entrega expressa"],
            "confianca": ["Ver avaliações", "Falar com vendedor", "Ver garantia"],
            "comparacao": ["Comparar produtos", "Ver diferenças", "Falar com especialista"],
            "disponibilidade": ["Confirmar estoque", "Ver alternativas", "Reservar produto"],
        }
        return actions_map.get(objection_type, ["Falar com atendente"])


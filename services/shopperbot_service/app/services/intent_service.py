"""Serviço de classificação de intenção"""
import re
from typing import Dict
from app.schemas.intent import IntentRequest, IntentResponse, IntentType, ExtractedEntity
from app.services.keyword_matcher import KeywordMatcher


class IntentService:
    """Classifica intenção do usuário"""
    
    def __init__(self):
        self.keyword_matcher = KeywordMatcher()
        self.intent_patterns = self._build_intent_patterns()
    
    def _build_intent_patterns(self) -> Dict[IntentType, list]:
        """Construir padrões de palavras-chave para cada intenção"""
        return {
            IntentType.BUY_NOW: [
                "quero comprar", "vou levar", "me vende", "quero esse", "compro agora",
                "aceito", "fechado", "eu quero", "me passa", "manda pra mim"
            ],
            IntentType.COMPARE: [
                "qual a diferença", "qual melhor", "compare", "diferença entre",
                "versus", "vs", "qual vale mais", "qual é melhor"
            ],
            IntentType.PRICE_CHECK: [
                "quanto custa", "qual o preço", "quanto é", "preço", "valor",
                "quanto sai", "quanto fica", "custa quanto"
            ],
            IntentType.AVAILABILITY: [
                "tem disponível", "tem em estoque", "tem ai", "você tem",
                "tem esse", "disponível", "tem pra vender"
            ],
            IntentType.URGENT: [
                "urgente", "preciso agora", "hoje", "rápido", "já",
                "emergência", "preciso urgente", "pode ser hoje"
            ],
            IntentType.GIFT: [
                "presente", "presentear", "pra dar de presente", "de presente",
                "aniversário", "aniversariante", "comemoração"
            ],
            IntentType.SUPPORT: [
                "problema", "não funciona", "reclamação", "erro",
                "ajuda", "suporte", "dúvida", "não entendi"
            ]
        }
    
    def classify(self, request: IntentRequest) -> IntentResponse:
        """Classifica a intenção do usuário"""
        message_lower = request.message.lower()
        
        # Calcular scores para cada intenção
        intent_scores: Dict[IntentType, float] = {}
        for intent_type, patterns in self.intent_patterns.items():
            score = self.keyword_matcher.match_score(message_lower, patterns)
            intent_scores[intent_type] = score
        
        # Determinar intent principal
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        intent_type = primary_intent[0]
        confidence = primary_intent[1]
        
        # Se confidence baixo, default para browsing
        if confidence < 0.3:
            intent_type = IntentType.JUST_BROWSING
            confidence = 0.5
        
        # Calcular urgency
        urgency = self._calculate_urgency(message_lower, intent_type)
        
        # Extrair entidades
        entities = self._extract_entities(request.message, intent_type)
        
        return IntentResponse(
            intent=intent_type,
            urgency=urgency,
            confidence=min(1.0, confidence),
            extracted_entities=entities,
            reasoning=f"Intent detectado: {intent_type.value} (confidence: {confidence:.2f})"
        )
    
    def _calculate_urgency(self, message: str, intent: IntentType) -> float:
        """Calcula nível de urgência"""
        if intent == IntentType.URGENT:
            return 0.9
        
        urgent_words = ["hoje", "agora", "urgente", "já", "rápido", "emergência"]
        if any(word in message for word in urgent_words):
            return 0.7
        
        if intent == IntentType.BUY_NOW:
            return 0.6
        
        return 0.3
    
    def _extract_entities(self, message: str, intent: IntentType) -> ExtractedEntity:
        """Extrai entidades da mensagem"""
        message_lower = message.lower()
        
        # Preços
        faixa_preco = None
        if any(word in message_lower for word in ["barato", "econômico", "em conta"]):
            faixa_preco = "barato"
        elif any(word in message_lower for word in ["caro", "caríssimo"]):
            faixa_preco = "caro"
        elif any(word in message_lower for word in ["médio", "normal"]):
            faixa_preco = "medio"
        
        # Quantidade
        quantidade = None
        qty_match = re.search(r'\b(\d+)\s*(unidades?|un|pç|pecas?|pacotes?)\b', message_lower)
        if qty_match:
            quantidade = int(qty_match.group(1))
        
        # Cidade/bairro (padrões simples)
        cidade = None
        bairro = None
        # Pode ser expandido com lista de cidades/bairros
        
        return ExtractedEntity(
            produto=None,  # Será preenchido pelo recommendation service
            categoria=None,
            faixa_preco=faixa_preco,
            cidade=cidade,
            bairro=bairro,
            quantidade=quantidade
        )


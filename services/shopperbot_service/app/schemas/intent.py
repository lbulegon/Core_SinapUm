"""Schemas para Intent Service"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from enum import Enum


class IntentType(str, Enum):
    """Tipos de intenção"""
    BUY_NOW = "buy_now"
    COMPARE = "compare"
    JUST_BROWSING = "just_browsing"
    PRICE_CHECK = "price_check"
    AVAILABILITY = "availability"
    URGENT = "urgent"
    GIFT = "gift"
    SUPPORT = "support"


class ContextType(str, Enum):
    """Tipo de contexto da conversa"""
    GROUP = "group"
    PRIVATE = "private"


class IntentRequest(BaseModel):
    """Payload para classificar intenção"""
    message: str = Field(..., min_length=1, max_length=1000)
    contexto: ContextType = ContextType.GROUP
    user_id: str
    group_id: Optional[str] = None
    estabelecimento_id: str
    conversation_history: Optional[List[str]] = []


class ExtractedEntity(BaseModel):
    """Entidades extraídas da mensagem"""
    produto: Optional[str] = None
    categoria: Optional[str] = None
    faixa_preco: Optional[str] = None  # "barato", "medio", "caro"
    cidade: Optional[str] = None
    bairro: Optional[str] = None
    quantidade: Optional[int] = None


class IntentResponse(BaseModel):
    """Resposta da classificação de intenção"""
    intent: IntentType
    urgency: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    extracted_entities: ExtractedEntity
    reasoning: Optional[str] = None


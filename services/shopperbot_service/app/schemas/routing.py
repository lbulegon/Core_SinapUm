"""Schemas para Conversation Router"""
from pydantic import BaseModel
from typing import Optional, Literal
from app.schemas.intent import IntentType, IntentResponse


class RouteRequest(BaseModel):
    """Payload para roteamento"""
    intent_payload: IntentResponse
    user_id: str
    group_id: str
    estabelecimento_id: str
    contexto: Optional[dict] = None


class RouteResponse(BaseModel):
    """Resposta do roteamento"""
    next_step: Literal["group_hint", "private_chat", "human_handoff"]
    confidence: float
    reasoning: str
    suggested_message: Optional[str] = None


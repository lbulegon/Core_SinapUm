"""Schemas para Objection Service"""
from pydantic import BaseModel, Field
from typing import Optional, List
from app.schemas.intent import IntentType


class ObjectionRequest(BaseModel):
    """Payload para responder objeção"""
    message: str = Field(..., min_length=1, max_length=1000)
    intent: IntentType
    product_id: Optional[str] = None
    contexto: Optional[dict] = None
    conversation_history: Optional[List[str]] = []


class ObjectionResponse(BaseModel):
    """Resposta para objeção"""
    resposta: str
    handoff_required: bool = False
    objection_type: Optional[str] = None  # "preco", "prazo", "confianca", "comparacao", "disponibilidade"
    suggested_actions: List[str] = []


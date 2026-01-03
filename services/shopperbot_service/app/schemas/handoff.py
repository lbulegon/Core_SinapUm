"""Schemas para Handoff Service"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class HandoffRequest(BaseModel):
    """Payload para handoff humano"""
    caso: str = Field(..., description="Descrição do caso")
    contexto: dict = Field(default_factory=dict)
    suggested_human_role: Literal["shopper", "keeper"] = "shopper"
    user_id: str
    group_id: Optional[str] = None
    estabelecimento_id: str
    urgency: float = Field(default=0.5, ge=0.0, le=1.0)


class HandoffResponse(BaseModel):
    """Resposta do handoff"""
    success: bool
    queue_id: str
    assigned_to: Optional[str] = None
    estimated_wait_time: Optional[int] = None  # segundos
    message: str


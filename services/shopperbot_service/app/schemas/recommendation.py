"""Schemas para Recommendation Service"""
from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.intent import IntentType, IntentResponse


class RecommendationFilter(BaseModel):
    """Filtros para recomendação"""
    estabelecimento_id: str
    categoria: Optional[str] = None
    faixa_preco: Optional[str] = None  # "barato", "medio", "caro"
    max_results: int = Field(default=5, ge=1, le=20)


class RecommendationRequest(BaseModel):
    """Payload para recomendar produtos"""
    intent_payload: IntentResponse
    filtros: RecommendationFilter
    contexto: Optional[dict] = None


class ProductHighlight(BaseModel):
    """Destaque de um produto na recomendação"""
    field: str  # "preco", "categoria", "popularidade", etc
    value: str
    match_reason: str


class RecommendedProduct(BaseModel):
    """Produto recomendado"""
    product_id: str
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str
    highlights: List[ProductHighlight] = []


class RecommendationResponse(BaseModel):
    """Resposta da recomendação"""
    products: List[RecommendedProduct]
    intent: IntentType
    total_candidates: int


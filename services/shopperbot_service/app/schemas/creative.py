"""Schemas para Creative Card Service"""
from pydantic import BaseModel, Field
from typing import Optional


class CardOverlay(BaseModel):
    """Dados para overlay no card"""
    nome: str
    preco: float
    cta: str = "Ver produto"
    promo: Optional[str] = None  # "10% OFF", etc
    cor_destaque: Optional[str] = "#667eea"  # Cor hex para elementos destacados


class CardRequest(BaseModel):
    """Payload para gerar card"""
    product_id: str
    overlay: CardOverlay
    imagem_original_url: Optional[str] = None  # Se não fornecido, busca do catálogo


class CardResponse(BaseModel):
    """Resposta da geração de card"""
    card_url: str
    product_id: str
    format: str = "png"
    width: int
    height: int


"""
Contratos públicos do Creative Engine Service
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CreativeContext:
    """Contexto para geração de criativos"""
    channel: str  # "status" | "group" | "private"
    locale: str = "pt-BR"
    tone: str = "direto"  # "direto" | "elegante" | "popular" | "premium" | "urgente"
    audience_hint: Optional[str] = None
    time_of_day: Optional[str] = None  # "morning" | "afternoon" | "night"
    stock_level: Optional[str] = None  # "low" | "normal" | "high"
    price_sensitivity: Optional[str] = None  # "low" | "medium" | "high"
    campaign_tag: Optional[str] = None


@dataclass
class CreativeBrief:
    """Brief de criativo gerado por estratégia"""
    headline: str
    angle: str
    bullets: List[str]
    cta: str
    urgency_text: Optional[str] = None
    scarcity_text: Optional[str] = None


@dataclass
class CreativeVariant:
    """Variante de criativo"""
    variant_id: str
    strategy: str
    channel: str
    image_url: Optional[str] = None
    text_short: Optional[str] = None
    text_medium: Optional[str] = None
    text_long: Optional[str] = None
    discourse: Optional[Dict[str, Any]] = None
    ctas: Optional[List[str]] = None


@dataclass
class CreativeResponse:
    """Resposta de geração de criativo"""
    creative_id: str
    variants: List[CreativeVariant]
    recommended_variant_id: str
    debug: Optional[Dict[str, Any]] = None


# Contratos de função (type hints para documentação)

def generate_creative(
    product_id: str,
    shopper_id: str,
    context: CreativeContext
) -> CreativeResponse:
    """
    Gera criativo principal para produto e shopper
    
    Args:
        product_id: ID do produto
        shopper_id: ID do shopper
        context: Contexto de geração
    
    Returns:
        CreativeResponse com criativo e variantes
    """
    pass


def generate_variants(
    creative_id: str,
    strategies: List[str],
    context: CreativeContext
) -> List[CreativeVariant]:
    """
    Gera variantes de um criativo usando estratégias específicas
    
    Args:
        creative_id: ID do criativo base
        strategies: Lista de estratégias a aplicar
        context: Contexto de geração
    
    Returns:
        Lista de variantes geradas
    """
    pass


def adapt_creative(
    variant_id: str,
    channel: str,
    context: CreativeContext
) -> Dict[str, Any]:
    """
    Adapta variante para canal específico
    
    Args:
        variant_id: ID da variante
        channel: Canal de destino
        context: Contexto de adaptação
    
    Returns:
        Payload adaptado para o canal
    """
    pass


def register_performance(
    event: Dict[str, Any]
) -> None:
    """
    Registra evento de performance
    
    Args:
        event: Evento de performance (VIEWED, RESPONDED, INTERESTED, etc)
    """
    pass


def recommend_next(
    shopper_id: str,
    product_id: str,
    context: CreativeContext
) -> CreativeResponse:
    """
    Recomenda próximo criativo baseado em aprendizado
    
    Args:
        shopper_id: ID do shopper
        product_id: ID do produto
        context: Contexto atual
    
    Returns:
        CreativeResponse com recomendação otimizada
    """
    pass

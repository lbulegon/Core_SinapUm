"""
Estratégia de preço - foco em valor e economia
"""
from typing import Dict, Any, Optional
from services.creative_engine_service.strategies.base import BaseStrategy
from services.creative_engine_service.contracts import CreativeBrief, CreativeContext


class PriceStrategy(BaseStrategy):
    """Estratégia focada em preço e valor"""
    
    @property
    def name(self) -> str:
        return "price"
    
    def generate_brief(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        performance_history: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """Gera brief focado em preço"""
        nome = product_data.get("nome", "")
        marca = product_data.get("marca", "")
        
        # Obter preço se disponível
        preco = self._extract_price(product_data)
        
        headline = f"Melhor preço: {marca} {nome}"
        if preco:
            headline = f"Por apenas R$ {preco:.2f}: {marca} {nome}"
        
        angle = "Valor e economia"
        
        bullets = [
            f"Preço especial: R$ {preco:.2f}" if preco else "Melhor preço do mercado",
            "Qualidade garantida",
            "Entrega rápida",
        ]
        
        urgency_text = None
        if context.stock_level == "low":
            urgency_text = "Últimas unidades disponíveis!"
        
        cta = "Garanta já pelo melhor preço!"
        
        return CreativeBrief(
            headline=headline,
            angle=angle,
            bullets=bullets,
            urgency_text=urgency_text,
            cta=cta
        )
    
    def _extract_price(self, product_data: Dict[str, Any]) -> Optional[float]:
        """Extrai preço do produto"""
        # Tentar diferentes campos de preço
        if "preco" in product_data:
            return float(product_data["preco"])
        if "preco_viagem" in product_data:
            return float(product_data["preco_viagem"])
        if "valor" in product_data:
            return float(product_data["valor"])
        return None

"""
Estratégia de escassez - foco em estoque limitado
"""
from typing import Dict, Any, Optional
from services.creative_engine_service.strategies.base import BaseStrategy
from services.creative_engine_service.contracts import CreativeBrief, CreativeContext


class ScarcityStrategy(BaseStrategy):
    """Estratégia focada em escassez e estoque limitado"""
    
    @property
    def name(self) -> str:
        return "scarcity"
    
    def generate_brief(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        performance_history: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """Gera brief focado em escassez"""
        nome = product_data.get("nome", "")
        marca = product_data.get("marca", "")
        
        headline = f"🔥 Últimas unidades: {marca} {nome}"
        
        angle = "Escassez e estoque limitado"
        
        scarcity_text = self._generate_scarcity_text(context)
        
        bullets = [
            "Estoque limitado",
            "Últimas unidades disponíveis",
            "Não perca esta oportunidade única",
        ]
        
        cta = "Garanta a sua antes que acabe!"
        
        return CreativeBrief(
            headline=headline,
            angle=angle,
            bullets=bullets,
            scarcity_text=scarcity_text,
            cta=cta
        )
    
    def _generate_scarcity_text(self, context: CreativeContext) -> str:
        """Gera texto de escassez baseado no contexto"""
        stock_level = context.stock_level
        
        if stock_level == "low":
            return "⚠️ Apenas algumas unidades restantes! Garanta já."
        elif stock_level == "normal":
            return "Estoque limitado. Garanta a sua enquanto há disponibilidade."
        else:
            return "Produto em alta demanda. Garanta a sua!"

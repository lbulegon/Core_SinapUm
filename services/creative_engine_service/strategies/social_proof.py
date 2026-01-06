"""
Estratégia de prova social - foco em popularidade e recomendações
"""
from typing import Dict, Any, Optional
from services.creative_engine_service.strategies.base import BaseStrategy
from services.creative_engine_service.contracts import CreativeBrief, CreativeContext


class SocialProofStrategy(BaseStrategy):
    """Estratégia focada em prova social e popularidade"""
    
    @property
    def name(self) -> str:
        return "social_proof"
    
    def generate_brief(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        performance_history: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """Gera brief focado em prova social"""
        nome = product_data.get("nome", "")
        marca = product_data.get("marca", "")
        
        headline = f"⭐ Mais vendido: {marca} {nome}"
        
        angle = "Prova social e popularidade"
        
        bullets = [
            "Mais vendido da categoria",
            "Recomendado por especialistas",
            "Aprovado por milhares de clientes",
        ]
        
        # Adicionar prova social se houver histórico
        if performance_history:
            views = performance_history.get("views", 0)
            orders = performance_history.get("orders", 0)
            if views > 0:
                bullets.append(f"Visualizado por {views} pessoas")
            if orders > 0:
                bullets.append(f"{orders} pedidos realizados")
        
        cta = "Junte-se aos clientes satisfeitos!"
        
        return CreativeBrief(
            headline=headline,
            angle=angle,
            bullets=bullets[:4],  # Limitar a 4
            cta=cta
        )

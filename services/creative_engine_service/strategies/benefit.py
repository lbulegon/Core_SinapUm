"""
Estratégia de benefícios - foco em valor e qualidade
"""
from typing import Dict, Any, Optional
from services.creative_engine_service.strategies.base import BaseStrategy
from services.creative_engine_service.contracts import CreativeBrief, CreativeContext


class BenefitStrategy(BaseStrategy):
    """Estratégia focada em benefícios e qualidade"""
    
    @property
    def name(self) -> str:
        return "benefit"
    
    def generate_brief(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        performance_history: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """Gera brief focado em benefícios"""
        nome = product_data.get("nome", "")
        marca = product_data.get("marca", "")
        descricao = product_data.get("descricao", "")
        categoria = product_data.get("categoria", "")
        volume_ml = product_data.get("volume_ml")
        
        headline = f"{marca} {nome}: Qualidade que você merece"
        
        angle = "Benefícios e qualidade premium"
        
        bullets = []
        
        if marca:
            bullets.append(f"Marca reconhecida: {marca}")
        
        if categoria:
            bullets.append(f"Categoria premium: {categoria}")
        
        if volume_ml:
            bullets.append(f"Volume generoso: {volume_ml}ml")
        
        if descricao:
            # Extrair benefício da descrição
            bullets.append("Qualidade excepcional")
        
        # Garantir pelo menos 2 bullets
        if len(bullets) < 2:
            bullets.extend([
                "Qualidade garantida",
                "Experiência única"
            ])
        
        cta = "Experimente a diferença!"
        
        return CreativeBrief(
            headline=headline,
            angle=angle,
            bullets=bullets[:4],  # Limitar a 4
            cta=cta
        )

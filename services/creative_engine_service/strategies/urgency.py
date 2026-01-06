"""
Estratégia de urgência - foco em tempo limitado
"""
from typing import Dict, Any, Optional
from services.creative_engine_service.strategies.base import BaseStrategy
from services.creative_engine_service.contracts import CreativeBrief, CreativeContext


class UrgencyStrategy(BaseStrategy):
    """Estratégia focada em urgência e tempo limitado"""
    
    @property
    def name(self) -> str:
        return "urgency"
    
    def generate_brief(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        performance_history: Optional[Dict[str, Any]] = None
    ) -> CreativeBrief:
        """Gera brief focado em urgência"""
        nome = product_data.get("nome", "")
        marca = product_data.get("marca", "")
        
        headline = f"⏰ Oferta por tempo limitado: {marca} {nome}"
        
        angle = "Urgência e tempo limitado"
        
        urgency_text = self._generate_urgency_text(context)
        
        bullets = [
            "Oferta válida por tempo limitado",
            "Não perca esta oportunidade",
            "Garanta já antes que acabe",
        ]
        
        cta = "Aproveite agora antes que acabe!"
        
        return CreativeBrief(
            headline=headline,
            angle=angle,
            bullets=bullets,
            urgency_text=urgency_text,
            cta=cta
        )
    
    def _generate_urgency_text(self, context: CreativeContext) -> str:
        """Gera texto de urgência baseado no contexto"""
        time_of_day = context.time_of_day
        
        if time_of_day == "morning":
            return "Oferta válida apenas hoje! Aproveite pela manhã."
        elif time_of_day == "afternoon":
            return "Últimas horas! Oferta termina ao final do dia."
        elif time_of_day == "night":
            return "Última chance hoje! Oferta válida até meia-noite."
        else:
            return "Oferta por tempo limitado! Não perca!"

"""
Gerador de discursos conversacionais
"""
import logging
from typing import Dict, Any, List
from services.creative_engine_service.contracts import CreativeContext

logger = logging.getLogger(__name__)


class DiscourseGenerator:
    """Gera argumentos conversacionais para criativos"""
    
    def generate(
        self,
        brief: Dict[str, Any],
        context: CreativeContext,
        product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Gera discurso conversacional completo
        
        Args:
            brief: Brief do criativo
            context: Contexto de geração
            product_data: Dados do produto
        
        Returns:
            Dict com opening, benefits, objections, cta
        """
        opening = self._generate_opening(brief, product_data, context)
        benefits = self._generate_benefits(brief, product_data)
        objections = self._generate_objections(product_data, context)
        cta = brief.get("cta", "Quer saber mais? Me chama!")
        
        return {
            "opening": opening,
            "benefits": benefits,
            "objections": objections,
            "cta": cta,
        }
    
    def _generate_opening(
        self,
        brief: Dict[str, Any],
        product_data: Dict[str, Any],
        context: CreativeContext
    ) -> str:
        """Gera frase de abertura"""
        headline = brief.get("headline", "")
        nome = product_data.get("nome", "")
        marca = product_data.get("marca", "")
        
        tone = context.tone
        
        if tone == "direto":
            return f"{headline} {marca} {nome}"
        elif tone == "elegante":
            return f"Apresento-lhes {marca} {nome}: {headline}"
        elif tone == "popular":
            return f"Olha só que achado! {headline} - {marca} {nome}"
        elif tone == "premium":
            return f"Exclusivo: {marca} {nome}. {headline}"
        elif tone == "urgente":
            return f"🔥 Atenção! {headline} - {marca} {nome}"
        else:
            return headline
    
    def _generate_benefits(
        self,
        brief: Dict[str, Any],
        product_data: Dict[str, Any]
    ) -> List[str]:
        """Gera lista de benefícios (2-4 bullets)"""
        bullets = brief.get("bullets", [])
        
        # Se não houver bullets no brief, gerar baseado no produto
        if not bullets:
            bullets = self._extract_benefits_from_product(product_data)
        
        # Limitar a 4 bullets
        return bullets[:4]
    
    def _extract_benefits_from_product(self, product_data: Dict[str, Any]) -> List[str]:
        """Extrai benefícios do produto quando não há no brief"""
        benefits = []
        
        marca = product_data.get("marca", "")
        if marca:
            benefits.append(f"Marca reconhecida: {marca}")
        
        categoria = product_data.get("categoria", "")
        if categoria:
            benefits.append(f"Categoria premium: {categoria}")
        
        volume = product_data.get("volume_ml")
        if volume:
            benefits.append(f"Volume generoso: {volume}ml")
        
        # Se não houver benefícios, usar genéricos
        if not benefits:
            benefits = [
                "Qualidade garantida",
                "Entrega rápida",
            ]
        
        return benefits
    
    def _generate_objections(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext
    ) -> List[Dict[str, str]]:
        """Gera quebra de objeções (2 objeções comuns)"""
        objections = []
        
        # Objeção de preço
        objections.append({
            "objection": "Muito caro",
            "response": "Entendo sua preocupação. Este produto oferece excelente custo-benefício e qualidade premium."
        })
        
        # Objeção de necessidade
        objections.append({
            "objection": "Não preciso agora",
            "response": "Perfeito para ter em estoque! Quando precisar, já estará disponível."
        })
        
        return objections[:2]

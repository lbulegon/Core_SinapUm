"""
Gerador de textos (copy) para criativos
"""
import logging
from typing import Dict, Any, List, Optional
from services.creative_engine_service.contracts import CreativeContext

logger = logging.getLogger(__name__)


class TextGenerator:
    """Gera textos adaptados por canal e tom"""
    
    TONE_TEMPLATES = {
        "direto": {
            "short": "{headline} {cta}",
            "medium": "{headline}\n\n{benefits}\n\n{cta}",
            "long": "{headline}\n\n{description}\n\n{benefits}\n\n{cta}",
        },
        "elegante": {
            "short": "{headline} {cta}",
            "medium": "{headline}\n\n{benefits}\n\n{cta}",
            "long": "{headline}\n\n{description}\n\n{benefits}\n\n{cta}",
        },
        "popular": {
            "short": "{headline} {cta}",
            "medium": "{headline}\n\n{benefits}\n\n{cta}",
            "long": "{headline}\n\n{description}\n\n{benefits}\n\n{cta}",
        },
        "premium": {
            "short": "{headline} {cta}",
            "medium": "{headline}\n\n{benefits}\n\n{cta}",
            "long": "{headline}\n\n{description}\n\n{benefits}\n\n{cta}",
        },
        "urgente": {
            "short": "🔥 {headline} {cta}",
            "medium": "🔥 {headline}\n\n{benefits}\n\n⏰ {urgency}\n\n{cta}",
            "long": "🔥 {headline}\n\n{description}\n\n{benefits}\n\n⏰ {urgency}\n\n{cta}",
        },
    }
    
    CHANNEL_LIMITS = {
        "status": {"max_chars": 250},
        "group": {"max_chars": 500},
        "private": {"max_chars": 1000},
    }
    
    def generate(
        self,
        brief: Dict[str, Any],
        context: CreativeContext,
        product_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Gera textos curto/médio/longo adaptados ao canal e tom
        
        Args:
            brief: Brief do criativo (headline, bullets, cta, etc)
            context: Contexto de geração
            product_data: Dados do produto
        
        Returns:
            Dict com text_short, text_medium, text_long
        """
        tone = context.tone
        channel = context.channel
        
        # Selecionar template baseado no tom
        templates = self.TONE_TEMPLATES.get(tone, self.TONE_TEMPLATES["direto"])
        
        # Preparar dados para template
        headline = brief.get("headline", product_data.get("nome", ""))
        description = product_data.get("descricao", "")
        benefits = "\n".join([f"• {b}" for b in brief.get("bullets", [])])
        cta = brief.get("cta", "Saiba mais")
        urgency = brief.get("urgency_text", "")
        
        # Gerar textos
        text_short = self._format_text(
            templates["short"],
            headline=headline,
            benefits=benefits[:50] if benefits else "",
            cta=cta,
            urgency=urgency
        )
        
        text_medium = self._format_text(
            templates["medium"],
            headline=headline,
            description=description[:150] if description else "",
            benefits=benefits,
            cta=cta,
            urgency=urgency
        )
        
        text_long = self._format_text(
            templates["long"],
            headline=headline,
            description=description,
            benefits=benefits,
            cta=cta,
            urgency=urgency
        )
        
        # Aplicar limites por canal
        max_chars = self.CHANNEL_LIMITS.get(channel, {}).get("max_chars", 1000)
        
        return {
            "text_short": text_short[:max_chars] if len(text_short) > max_chars else text_short,
            "text_medium": text_medium[:max_chars] if len(text_medium) > max_chars else text_medium,
            "text_long": text_long[:max_chars] if len(text_long) > max_chars else text_long,
        }
    
    def _format_text(self, template: str, **kwargs) -> str:
        """Formata template com kwargs"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Template key missing: {e}, using placeholder")
            return template.replace(f"{{{e.args[0]}}}", "")
    
    def _apply_tone_style(self, text: str, tone: str) -> str:
        """Aplica estilo do tom ao texto"""
        if tone == "elegante":
            # Remover emojis, usar linguagem mais formal
            text = text.replace("🔥", "").replace("⏰", "")
        elif tone == "popular":
            # Adicionar emojis, linguagem mais casual
            if "🔥" not in text:
                text = f"🔥 {text}"
        elif tone == "urgente":
            # Adicionar elementos de urgência
            if "⏰" not in text:
                text = f"⏰ {text}"
        
        return text.strip()

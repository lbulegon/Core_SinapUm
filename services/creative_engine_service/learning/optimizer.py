"""
Optimizer - reordena recomendações e ajusta pesos por contexto
"""
import logging
from typing import Dict, Any, List, Optional
from services.creative_engine_service.contracts import CreativeContext, CreativeVariant

logger = logging.getLogger(__name__)


class CreativeOptimizer:
    """Otimiza recomendações baseado em aprendizado"""
    
    # Pesos por estratégia por canal (heurístico MVP)
    STRATEGY_WEIGHTS = {
        "status": {
            "price": 0.3,
            "benefit": 0.2,
            "urgency": 0.3,
            "scarcity": 0.2,
            "social_proof": 0.0,
        },
        "group": {
            "price": 0.4,
            "benefit": 0.2,
            "urgency": 0.2,
            "scarcity": 0.1,
            "social_proof": 0.1,
        },
        "private": {
            "price": 0.2,
            "benefit": 0.4,
            "urgency": 0.1,
            "scarcity": 0.1,
            "social_proof": 0.2,
        },
    }
    
    def optimize_recommendations(
        self,
        variants: List[CreativeVariant],
        context: CreativeContext,
        performance_metrics: Optional[Dict[str, Dict[str, float]]] = None
    ) -> List[CreativeVariant]:
        """
        Reordena variantes baseado em canal, contexto e métricas
        
        Args:
            variants: Lista de variantes
            context: Contexto atual
            performance_metrics: Métricas de performance (opcional)
        
        Returns:
            Lista de variantes reordenada
        """
        if not variants:
            return []
        
        # Calcular score para cada variante
        scored_variants = []
        for variant in variants:
            score = self._calculate_variant_score(
                variant,
                context,
                performance_metrics
            )
            scored_variants.append((score, variant))
        
        # Ordenar por score (maior primeiro)
        scored_variants.sort(key=lambda x: x[0], reverse=True)
        
        # Retornar apenas variantes (sem score)
        return [variant for _, variant in scored_variants]
    
    def _calculate_variant_score(
        self,
        variant: CreativeVariant,
        context: CreativeContext,
        performance_metrics: Optional[Dict[str, Dict[str, float]]] = None
    ) -> float:
        """Calcula score de uma variante"""
        channel = context.channel
        strategy = variant.strategy
        
        # Peso base da estratégia para o canal
        base_weight = self.STRATEGY_WEIGHTS.get(channel, {}).get(strategy, 0.2)
        
        # Ajustar baseado em performance se disponível
        performance_score = 0.5  # Default neutro
        if performance_metrics and variant.variant_id in performance_metrics:
            metrics = performance_metrics[variant.variant_id]
            performance_score = metrics.get("engagement_score", 0.5)
        
        # Score final = peso base * performance
        final_score = base_weight * (0.5 + performance_score)
        
        # Ajustes contextuais
        if context.price_sensitivity == "high" and strategy == "price":
            final_score *= 1.2
        elif context.stock_level == "low" and strategy == "scarcity":
            final_score *= 1.2
        elif context.tone == "urgente" and strategy == "urgency":
            final_score *= 1.1
        
        return final_score
    
    def adjust_strategy_weights(
        self,
        channel: str,
        performance_data: Dict[str, Dict[str, float]]
    ) -> Dict[str, float]:
        """
        Ajusta pesos de estratégias baseado em performance (futuro: ML)
        
        Args:
            channel: Canal
            performance_data: Dados de performance por estratégia
        
        Returns:
            Dict com pesos ajustados
        """
        # MVP: Retornar pesos padrão
        # Em produção: usar ML para ajustar dinamicamente
        return self.STRATEGY_WEIGHTS.get(channel, {
            "price": 0.25,
            "benefit": 0.25,
            "urgency": 0.25,
            "scarcity": 0.25,
            "social_proof": 0.0,
        })

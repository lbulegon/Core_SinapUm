"""
Scorer - calcula métricas de performance por variante
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class CreativeScorer:
    """Calcula métricas de performance de criativos"""
    
    def calculate_metrics(
        self,
        variant_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calcula métricas de performance para uma variante
        
        Args:
            variant_id: ID da variante
            performance_data: Dados de performance agregados
        
        Returns:
            Dict com métricas calculadas
        """
        views = performance_data.get("views", 0)
        responses = performance_data.get("responses", 0)
        interests = performance_data.get("interests", 0)
        orders = performance_data.get("orders", 0)
        conversions = performance_data.get("conversions", 0)
        
        # Calcular taxas
        response_rate = (responses / views) if views > 0 else 0.0
        interest_rate = (interests / views) if views > 0 else 0.0
        conversion_rate = (conversions / views) if views > 0 else 0.0
        
        # Calcular engagement score (ponderado)
        engagement_score = (
            response_rate * 0.3 +
            interest_rate * 0.4 +
            conversion_rate * 0.3
        )
        
        # Calcular confidence index (baseado em volume)
        total_events = views + responses + interests + orders
        confidence_index = min(total_events / 100.0, 1.0)  # Máximo 1.0 com 100+ eventos
        
        return {
            "variant_id": variant_id,
            "response_rate": round(response_rate, 4),
            "interest_rate": round(interest_rate, 4),
            "conversion_rate": round(conversion_rate, 4),
            "engagement_score": round(engagement_score, 4),
            "confidence_index": round(confidence_index, 4),
            "total_views": views,
            "total_responses": responses,
            "total_interests": interests,
            "total_orders": orders,
            "total_conversions": conversions,
        }
    
    def compare_variants(
        self,
        variants_metrics: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Compara métricas de múltiplas variantes
        
        Args:
            variants_metrics: Dict com variant_id -> métricas
        
        Returns:
            Dict com ranking e análise
        """
        if not variants_metrics:
            return {"ranking": [], "best_variant": None}
        
        # Ordenar por engagement_score
        ranked = sorted(
            variants_metrics.items(),
            key=lambda x: x[1].get("engagement_score", 0),
            reverse=True
        )
        
        ranking = [{"variant_id": v_id, "score": metrics["engagement_score"]} 
                  for v_id, metrics in ranked]
        
        best_variant = ranked[0][0] if ranked else None
        
        return {
            "ranking": ranking,
            "best_variant": best_variant,
            "total_variants": len(variants_metrics),
        }

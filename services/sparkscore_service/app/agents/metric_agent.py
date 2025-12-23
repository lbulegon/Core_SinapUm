"""
Agente Métrico - Probabilidade de engajamento e conversão
"""

from typing import Dict, Optional


class MetricAgent:
    """
    Agente especializado em análise métrica
    - Probabilidade de engajamento
    - Probabilidade de conversão
    - Métricas de performance
    """
    
    def analyze(
        self,
        stimulus: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Analisa estímulo do ponto de vista métrico
        
        Returns:
            Dict com análise métrica
        """
        text = stimulus.get('text', '').lower()
        
        # Probabilidade de engajamento
        engagement_prob = self._calculate_engagement_probability(text, context)
        
        # Probabilidade de conversão
        conversion_prob = self._calculate_conversion_probability(text, context)
        
        # Métricas de qualidade
        quality_metrics = self._calculate_quality_metrics(text, context)
        
        return {
            'engagement_probability': engagement_prob,
            'conversion_probability': conversion_prob,
            'quality_metrics': quality_metrics,
            'overall_metric_score': (
                engagement_prob * 0.4 +
                conversion_prob * 0.4 +
                quality_metrics['overall'] * 0.2
            )
        }
    
    def _calculate_engagement_probability(
        self,
        text: str,
        context: Optional[Dict]
    ) -> float:
        """Calcula probabilidade de engajamento"""
        score = 0.0
        
        # Fatores de engajamento
        engagement_factors = {
            'call_to_action': ['clique', 'compre', 'acesse', 'baixe', 'cadastre'],
            'urgency': ['urgente', 'agora', 'hoje', 'limitado', 'últimas'],
            'curiosity': ['descubra', 'saiba', 'veja', 'revele', 'surpreenda'],
            'social_proof': ['milhares', 'milhões', 'todos', 'comunidade', 'popular']
        }
        
        for factor, keywords in engagement_factors.items():
            matches = sum(1 for kw in keywords if kw in text)
            factor_score = min(matches / len(keywords), 1.0)
            score += factor_score * 0.25
        
        # Ajustar baseado em contexto histórico
        if context:
            historical_engagement = context.get('historical_engagement', 0.5)
            score = (score * 0.7) + (historical_engagement * 0.3)
        
        return min(score, 1.0)
    
    def _calculate_conversion_probability(
        self,
        text: str,
        context: Optional[Dict]
    ) -> float:
        """Calcula probabilidade de conversão"""
        score = 0.0
        
        # Fatores de conversão
        conversion_factors = {
            'value_proposition': ['benefício', 'vantagem', 'ganho', 'economia', 'lucro'],
            'trust_signals': ['garantia', 'seguro', 'confiável', 'certificado', 'aprovado'],
            'simplicity': ['fácil', 'simples', 'rápido', 'automático', 'instantâneo'],
            'exclusivity': ['exclusivo', 'único', 'limitado', 'especial', 'VIP']
        }
        
        for factor, keywords in conversion_factors.items():
            matches = sum(1 for kw in keywords if kw in text)
            factor_score = min(matches / len(keywords), 1.0)
            score += factor_score * 0.25
        
        # Ajustar baseado em contexto histórico
        if context:
            historical_conversion = context.get('historical_conversion', 0.3)
            score = (score * 0.7) + (historical_conversion * 0.3)
        
        return min(score, 1.0)
    
    def _calculate_quality_metrics(
        self,
        text: str,
        context: Optional[Dict]
    ) -> Dict:
        """Calcula métricas de qualidade"""
        metrics = {}
        
        # Comprimento adequado (não muito curto, não muito longo)
        length = len(text.split())
        if 10 <= length <= 100:
            metrics['length_score'] = 1.0
        elif length < 10:
            metrics['length_score'] = length / 10.0
        else:
            metrics['length_score'] = max(0.0, 1.0 - (length - 100) / 100.0)
        
        # Clareza (baixa ambiguidade)
        ambiguous_words = ['talvez', 'possivelmente', 'pode ser', 'talvez']
        ambiguous_count = sum(1 for word in ambiguous_words if word in text)
        metrics['clarity_score'] = max(0.0, 1.0 - (ambiguous_count / len(text.split()) * 10))
        
        # Relevância (baseado em contexto)
        if context:
            relevance_keywords = context.get('relevance_keywords', [])
            if relevance_keywords:
                matches = sum(1 for kw in relevance_keywords if kw in text.lower())
                metrics['relevance_score'] = min(matches / len(relevance_keywords), 1.0)
            else:
                metrics['relevance_score'] = 0.5
        else:
            metrics['relevance_score'] = 0.5
        
        # Score geral de qualidade
        metrics['overall'] = (
            metrics['length_score'] * 0.3 +
            metrics['clarity_score'] * 0.4 +
            metrics['relevance_score'] * 0.3
        )
        
        return metrics


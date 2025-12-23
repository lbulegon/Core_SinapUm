"""
Agente Psicológico - Análise de atração, risco e ruído
"""

from typing import Dict, Optional
import re


class PsychoAgent:
    """
    Agente especializado em análise psicológica
    - Atração (atração emocional, interesse)
    - Risco (percepção de risco, medo)
    - Ruído (interferência, confusão)
    """
    
    def analyze(
        self,
        stimulus: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Analisa estímulo do ponto de vista psicológico
        
        Returns:
            Dict com análise psicológica
        """
        text = stimulus.get('text', '').lower()
        
        # Análise de atração
        attraction = self._analyze_attraction(text)
        
        # Análise de risco
        risk = self._analyze_risk(text)
        
        # Análise de ruído
        noise = self._analyze_noise(text, context)
        
        # Intensidade emocional
        emotional_intensity = self._calculate_emotional_intensity(text)
        
        return {
            'attraction_score': attraction['score'],
            'attraction_factors': attraction['factors'],
            'risk_score': risk['score'],
            'risk_factors': risk['factors'],
            'noise_score': noise['score'],
            'noise_factors': noise['factors'],
            'emotional_intensity': emotional_intensity,
            'overall_psycho_score': self._calculate_overall_score(
                attraction['score'],
                risk['score'],
                noise['score']
            )
        }
    
    def _analyze_attraction(self, text: str) -> Dict:
        """Analisa fatores de atração"""
        attraction_keywords = {
            'positive_emotions': ['amor', 'alegria', 'felicidade', 'prazer', 'satisfação'],
            'desire': ['quero', 'desejo', 'preciso', 'vou', 'vou ter'],
            'benefits': ['benefício', 'vantagem', 'ganho', 'lucro', 'sucesso'],
            'exclusivity': ['exclusivo', 'único', 'especial', 'limitado', 'raro']
        }
        
        factors = {}
        total_score = 0.0
        
        for factor, keywords in attraction_keywords.items():
            matches = sum(1 for kw in keywords if kw in text)
            factor_score = min(matches / len(keywords), 1.0)
            factors[factor] = factor_score
            total_score += factor_score
        
        # Normalizar score
        attraction_score = min(total_score / len(attraction_keywords), 1.0)
        
        return {
            'score': attraction_score,
            'factors': factors
        }
    
    def _analyze_risk(self, text: str) -> Dict:
        """Analisa fatores de risco percebido"""
        risk_keywords = {
            'fear': ['medo', 'perigo', 'risco', 'ameaça', 'preocupação'],
            'uncertainty': ['talvez', 'pode ser', 'incerto', 'dúvida', 'não sei'],
            'loss': ['perder', 'perda', 'falha', 'erro', 'problema'],
            'negative_outcomes': ['ruim', 'pior', 'negativo', 'fracasso', 'derrota']
        }
        
        factors = {}
        total_score = 0.0
        
        for factor, keywords in risk_keywords.items():
            matches = sum(1 for kw in keywords if kw in text)
            factor_score = min(matches / len(keywords), 1.0)
            factors[factor] = factor_score
            total_score += factor_score
        
        # Normalizar score
        risk_score = min(total_score / len(risk_keywords), 1.0)
        
        return {
            'score': risk_score,
            'factors': factors
        }
    
    def _analyze_noise(self, text: str, context: Optional[Dict]) -> Dict:
        """Analisa fatores de ruído (interferência)"""
        noise_factors = {}
        
        # Ruído por complexidade (muitas palavras diferentes)
        words = text.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            # Alta diversidade = mais ruído
            noise_factors['complexity'] = unique_ratio
        else:
            noise_factors['complexity'] = 0.0
        
        # Ruído por ambiguidade (palavras ambíguas)
        ambiguous_words = ['pode', 'talvez', 'possivelmente', 'talvez', 'talvez']
        ambiguous_count = sum(1 for word in ambiguous_words if word in text)
        noise_factors['ambiguity'] = min(ambiguous_count / len(ambiguous_words), 1.0)
        
        # Ruído por falta de contexto
        if context:
            context_richness = len(context) / 10.0  # Normalizar
            noise_factors['context_lack'] = 1.0 - min(context_richness, 1.0)
        else:
            noise_factors['context_lack'] = 1.0
        
        # Score total de ruído
        noise_score = sum(noise_factors.values()) / len(noise_factors)
        
        return {
            'score': min(noise_score, 1.0),
            'factors': noise_factors
        }
    
    def _calculate_emotional_intensity(self, text: str) -> float:
        """Calcula intensidade emocional"""
        emotional_keywords = [
            'amor', 'ódio', 'medo', 'alegria', 'tristeza', 'raiva',
            'paixão', 'pânico', 'euforia', 'desespero', 'esperança'
        ]
        
        matches = sum(1 for kw in emotional_keywords if kw in text)
        intensity = min(matches / len(emotional_keywords), 1.0)
        
        # Intensificadores
        intensifiers = ['muito', 'extremamente', 'totalmente', 'completamente']
        intensifier_count = sum(1 for word in intensifiers if word in text)
        intensity += min(intensifier_count * 0.1, 0.3)
        
        return min(intensity, 1.0)
    
    def _calculate_overall_score(
        self,
        attraction: float,
        risk: float,
        noise: float
    ) -> float:
        """
        Calcula score psicológico geral
        Alta atração + Baixo risco + Baixo ruído = Alto score
        """
        # Normalizar: risco e ruído são negativos
        normalized_risk = 1.0 - risk
        normalized_noise = 1.0 - noise
        
        # Média ponderada
        overall = (
            attraction * 0.5 +
            normalized_risk * 0.3 +
            normalized_noise * 0.2
        )
        
        return min(max(overall, 0.0), 1.0)


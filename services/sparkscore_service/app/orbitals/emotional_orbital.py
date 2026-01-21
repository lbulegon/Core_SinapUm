"""
Orbital Emocional - Análise de valência, urgência e tom emocional
"""

from typing import Dict
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.orbital_result import OrbitalResult


class EmotionalOrbital(BaseOrbital):
    """
    Orbital Emocional - Analisa:
    - Valência (positivo/negativo)
    - Urgência/arousal
    - Tom emocional geral
    """
    
    def __init__(self):
        super().__init__(
            orbital_id="emotional",
            name="Orbital Emocional",
            version="1.0.0"
        )
        
        # Keywords positivas
        self.positive_keywords = [
            "oferta", "promoção", "ganhe", "imperdível", "melhor", 
            "economize", "desconto", "grátis", "exclusivo", "especial",
            "incrível", "fantástico", "ótimo", "excelente", "super"
        ]
        
        # Keywords de urgência/arousal
        self.urgency_keywords = [
            "hoje", "agora", "última chance", "só hoje", "corre", 
            "rápido", "urgente", "limitado", "acabando", "aproveite",
            "não perca", "venha já", "imediatamente"
        ]
        
        # Keywords negativas (apenas para controle/contradição)
        self.negative_keywords = [
            "problema", "atenção", "alerta grave", "cuidado", "perigo"
        ]
    
    def analyze(self, payload: Dict) -> OrbitalResult:
        """
        Analisa payload do ponto de vista emocional
        """
        text = self.extract_text_content(payload)
        
        # Features brutas
        raw_features = {}
        
        # 1. Valência (positivo)
        positive_count = self.detect_keywords(text, self.positive_keywords)
        positive_score = min(positive_count / len(self.positive_keywords), 1.0)
        raw_features["positive_score"] = positive_score
        raw_features["positive_keywords_found"] = positive_count
        
        # 2. Urgência/arousal
        urgency_count = self.detect_keywords(text, self.urgency_keywords)
        urgency_score = min(urgency_count / len(self.urgency_keywords), 1.0)
        raw_features["urgency_score"] = urgency_score
        raw_features["urgency_keywords_found"] = urgency_count
        
        # 3. Negatividade (controle)
        negative_count = self.detect_keywords(text, self.negative_keywords)
        negative_score = min(negative_count / len(self.negative_keywords), 1.0)
        raw_features["negative_score"] = negative_score
        raw_features["negative_keywords_found"] = negative_count
        
        # 4. Clareza/ambiguidade
        ambiguity_score = self._calculate_ambiguity(positive_score, negative_score)
        raw_features["ambiguity_score"] = ambiguity_score
        
        # 5. Calcular score
        score = self._calculate_score(positive_score, urgency_score, ambiguity_score, negative_score)
        score = self.clamp_score(score)
        
        # 6. Calcular confidence
        confidence = self._calculate_confidence(positive_count, urgency_count, negative_count)
        confidence = self.clamp_confidence(confidence)
        
        # 7. Top features
        top_features = []
        if positive_score > 0.3:
            top_features.append("positive_tone")
        if urgency_score > 0.3:
            top_features.append("urgency_detected")
        if ambiguity_score < 0.3:
            top_features.append("low_ambiguity")
        
        # 8. Rationale
        rationale_parts = []
        if positive_score > 0.5:
            rationale_parts.append(f"tom positivo forte ({positive_count} keywords)")
        elif positive_score > 0.2:
            rationale_parts.append("tom positivo moderado")
        else:
            rationale_parts.append("tom positivo fraco")
        
        if urgency_score > 0.5:
            rationale_parts.append(f"alta urgência detectada ({urgency_count} keywords)")
        elif urgency_score > 0.2:
            rationale_parts.append("urgência moderada")
        
        if ambiguity_score > 0.5:
            rationale_parts.append("ambiguidade detectada (mistura contraditória)")
        elif ambiguity_score < 0.3:
            rationale_parts.append("clareza emocional")
        
        rationale = ". ".join(rationale_parts) if rationale_parts else "Análise emocional básica"
        
        return OrbitalResult(
            orbital_id=self.orbital_id,
            name=self.name,
            status="active",
            score=score,
            confidence=confidence,
            rationale=rationale,
            top_features=top_features,
            raw_features=raw_features,
            version=self.version
        )
    
    def _calculate_ambiguity(self, positive_score: float, negative_score: float) -> float:
        """
        Calcula ambiguidade baseada em mistura de sinais contraditórios
        
        Args:
            positive_score: Score de positividade
            negative_score: Score de negatividade
        
        Returns:
            Score de ambiguidade (0-1, onde 1 = muito ambíguo)
        """
        # Ambiguidade alta se há tanto positivo quanto negativo
        if positive_score > 0.3 and negative_score > 0.3:
            return 0.8  # Alta ambiguidade
        elif positive_score > 0.1 and negative_score > 0.1:
            return 0.5  # Ambiguidade moderada
        else:
            return 0.2  # Baixa ambiguidade
    
    def _calculate_score(
        self, 
        positive_score: float, 
        urgency_score: float, 
        ambiguity_score: float,
        negative_score: float
    ) -> float:
        """
        Calcula score final (0-100)
        
        Heurística:
        - Base: 70 se tom positivo + clareza
        - Penaliza ambiguidade
        - Penaliza negatividade (se presente)
        """
        score = 70.0
        
        # Bonus por positividade
        score += 15.0 * positive_score
        
        # Bonus por urgência (moderado)
        score += 10.0 * urgency_score
        
        # Penaliza ambiguidade
        score -= 20.0 * ambiguity_score
        
        # Penaliza negatividade (se presente)
        if negative_score > 0.2:
            score -= 15.0 * negative_score
        
        return score
    
    def _calculate_confidence(
        self, 
        positive_count: int, 
        urgency_count: int, 
        negative_count: int
    ) -> float:
        """
        Calcula confidence (0-1)
        
        Base: 0.45-0.65 dependendo de presença de termos fortes
        """
        confidence = 0.45
        
        # Mais termos = mais confidence
        total_terms = positive_count + urgency_count
        
        if total_terms > 3:
            confidence = 0.65
        elif total_terms > 1:
            confidence = 0.55
        else:
            confidence = 0.45
        
        # Se há negatividade, reduz um pouco (sinal misto)
        if negative_count > 0:
            confidence -= 0.05
        
        return confidence


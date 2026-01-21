"""
Orbital Cognitivo - Análise de clareza, densidade e adequação ao formato
"""

from typing import Dict
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.orbital_result import OrbitalResult


class CognitiveOrbital(BaseOrbital):
    """
    Orbital Cognitivo - Analisa:
    - Densidade de palavras (adequação ao formato)
    - Clareza de objetivo
    - Complexidade cognitiva
    """
    
    def __init__(self):
        super().__init__(
            orbital_id="cognitive",
            name="Orbital Cognitivo",
            version="1.0.0"
        )
        
        # Limites ideais de palavras por formato
        self.ideal_word_limits = {
            "whatsapp_status": 12,
            "whatsapp_story": 12,
            "instagram_story": 15,
            "instagram_feed": 20,
            "facebook_feed": 25,
            "default": 20
        }
    
    def analyze(self, payload: Dict) -> OrbitalResult:
        """
        Analisa payload do ponto de vista cognitivo
        """
        text = self.extract_text_content(payload)
        context = self.extract_context(payload)
        format_type = context.get("format", "default")
        goal = self.extract_goal(payload)
        
        # Features brutas
        raw_features = {}
        
        # 1. Contagem de palavras
        word_count = self.count_words(text)
        raw_features["word_count"] = word_count
        raw_features["text_length"] = len(text)
        
        # 2. Densidade por formato
        density_score = self._calculate_density_score(word_count, format_type)
        raw_features["density_score"] = density_score
        raw_features["format"] = format_type
        raw_features["ideal_limit"] = self.ideal_word_limits.get(format_type, self.ideal_word_limits["default"])
        
        # 3. Clareza de objetivo
        goal_clarity = self._calculate_goal_clarity(text, goal)
        raw_features["goal_clarity"] = goal_clarity
        raw_features["goal"] = goal
        
        # 4. Calcular score
        score = self._calculate_score(density_score, goal_clarity)
        score = self.clamp_score(score)
        
        # 5. Calcular confidence
        confidence = self._calculate_confidence(word_count, goal_clarity)
        confidence = self.clamp_confidence(confidence)
        
        # 6. Top features
        top_features = []
        if density_score > 0.7:
            top_features.append("optimal_density")
        if goal_clarity > 0.7:
            top_features.append("clear_goal")
        if word_count <= self.ideal_word_limits.get(format_type, 20):
            top_features.append("appropriate_length")
        
        # 7. Rationale
        rationale_parts = []
        
        ideal_limit = self.ideal_word_limits.get(format_type, self.ideal_word_limits["default"])
        if word_count <= ideal_limit:
            rationale_parts.append(f"densidade adequada ({word_count} palavras para {format_type})")
        elif word_count <= ideal_limit * 1.5:
            rationale_parts.append(f"densidade moderada ({word_count} palavras, ideal: {ideal_limit})")
        else:
            rationale_parts.append(f"densidade alta ({word_count} palavras, ideal: {ideal_limit})")
        
        if goal:
            if goal_clarity > 0.7:
                rationale_parts.append("objetivo claro refletido no texto")
            elif goal_clarity > 0.4:
                rationale_parts.append("objetivo parcialmente refletido")
            else:
                rationale_parts.append("objetivo não refletido claramente no texto")
        else:
            rationale_parts.append("sem objetivo definido")
        
        rationale = ". ".join(rationale_parts) if rationale_parts else "Análise cognitiva básica"
        
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
    
    def _calculate_density_score(self, word_count: int, format_type: str) -> float:
        """
        Calcula score de densidade (0-1, onde 1 = ideal)
        
        Args:
            word_count: Número de palavras
            format_type: Tipo de formato (ex: "whatsapp_status")
        
        Returns:
            Score de densidade
        """
        ideal_limit = self.ideal_word_limits.get(format_type, self.ideal_word_limits["default"])
        
        if word_count == 0:
            return 0.0
        
        if word_count <= ideal_limit:
            # Dentro do ideal: score alto
            return 1.0
        elif word_count <= ideal_limit * 1.5:
            # Moderadamente acima: score médio
            excess = word_count - ideal_limit
            penalty = excess / ideal_limit
            return max(0.5, 1.0 - penalty * 0.5)
        else:
            # Muito acima: score baixo
            excess = word_count - ideal_limit
            penalty = min(1.0, excess / ideal_limit)
            return max(0.0, 0.5 - penalty * 0.5)
    
    def _calculate_goal_clarity(self, text: str, goal: str) -> float:
        """
        Calcula clareza de objetivo (0-1)
        
        Args:
            text: Texto da peça
            goal: Goal da peça
        
        Returns:
            Score de clareza
        """
        if not goal:
            return 0.5  # Neutro se não há goal
        
        # Verificar se goal está refletido no texto
        # Para goals específicos, verificar keywords relacionadas
        goal_indicators = {
            "whatsapp_click": ["whatsapp", "zap", "chame", "fale"],
            "link_click": ["link", "acesse", "saiba", "confira"],
            "purchase": ["compre", "garanta", "adquira"],
            "download": ["baixe", "download"],
            "signup": ["cadastre", "inscreva"]
        }
        
        indicators = goal_indicators.get(goal, [])
        if not indicators:
            return 0.5  # Goal desconhecido
        
        # Verificar se algum indicador aparece
        matches = self.detect_keywords(text, indicators)
        if matches > 0:
            return 0.8  # Alto se há match
        else:
            return 0.3  # Baixo se não há match
    
    def _calculate_score(self, density_score: float, goal_clarity: float) -> float:
        """
        Calcula score final (0-100)
        
        Heurística:
        - Base: 75
        - Penaliza se overlay muito longo (densidade baixa)
        - Penaliza se não há objetivo claro
        """
        score = 75.0
        
        # Bonus por densidade adequada
        score += 15.0 * density_score
        
        # Bonus por clareza de objetivo
        score += 10.0 * goal_clarity
        
        # Penaliza densidade baixa
        if density_score < 0.5:
            score -= 20.0 * (0.5 - density_score)
        
        # Penaliza falta de objetivo claro
        if goal_clarity < 0.5:
            score -= 15.0 * (0.5 - goal_clarity)
        
        return score
    
    def _calculate_confidence(self, word_count: int, goal_clarity: float) -> float:
        """
        Calcula confidence (0-1)
        
        Base: 0.5-0.65 dependendo de informações disponíveis
        """
        confidence = 0.5
        
        # Mais palavras = mais informação = mais confidence
        if word_count > 10:
            confidence = 0.6
        elif word_count > 5:
            confidence = 0.55
        
        # Goal claro aumenta confidence
        if goal_clarity > 0.7:
            confidence += 0.05
        
        return confidence


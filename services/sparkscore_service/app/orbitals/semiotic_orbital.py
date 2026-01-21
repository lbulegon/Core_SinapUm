"""
Orbital Semiótico - Análise de CTA, coerência e redundância
"""

from typing import Dict
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.orbital_result import OrbitalResult


class SemioticOrbital(BaseOrbital):
    """
    Orbital Semiótico - Analisa:
    - Detecção de CTA (Call-to-Action)
    - Coerência entre goal e texto
    - Redundância (palavras repetidas)
    """
    
    def __init__(self):
        super().__init__(
            orbital_id="semiotic",
            name="Orbital Semiótico",
            version="1.0.0"
        )
        
        # Keywords de CTA em português
        self.cta_keywords = [
            "clique", "chame", "peça", "agora", "whatsapp", "fale", 
            "compre", "garanta", "saiba mais", "link", "acesse", 
            "baixe", "cadastre", "entre", "veja", "confira"
        ]
    
    def analyze(self, payload: Dict) -> OrbitalResult:
        """
        Analisa payload do ponto de vista semiótico
        """
        text = self.extract_text_content(payload)
        goal = self.extract_goal(payload)
        context = self.extract_context(payload)
        format_type = context.get("format", "")
        
        # Features brutas
        raw_features = {}
        
        # 1. Detecção de CTA
        cta_detected = self.detect_keywords(text, self.cta_keywords) > 0
        cta_keywords_found = self.detect_keywords(text, self.cta_keywords)
        raw_features["cta_detected"] = cta_detected
        raw_features["cta_keywords_found"] = cta_keywords_found
        
        # 2. Coerência goal vs texto
        goal_coherence = self._calculate_goal_coherence(text, goal)
        raw_features["goal_match"] = goal_coherence
        
        # 3. Redundância
        redundancy_score = self._calculate_redundancy(text)
        raw_features["redundancy_score"] = redundancy_score
        
        # 4. Calcular score
        score = self._calculate_score(cta_detected, goal_coherence, redundancy_score)
        score = self.clamp_score(score)
        
        # 5. Calcular confidence
        confidence = self._calculate_confidence(cta_detected, goal_coherence, cta_keywords_found)
        confidence = self.clamp_confidence(confidence)
        
        # 6. Top features
        top_features = []
        if cta_detected:
            top_features.append("cta_detected")
        if goal_coherence > 0.7:
            top_features.append("goal_coherence")
        if redundancy_score < 0.3:
            top_features.append("low_redundancy")
        
        # 7. Rationale
        rationale_parts = []
        if cta_detected:
            rationale_parts.append(f"CTA detectado ({cta_keywords_found} keywords)")
        else:
            rationale_parts.append("CTA não detectado")
        
        if goal:
            if goal_coherence > 0.7:
                rationale_parts.append("boa coerência entre goal e texto")
            elif goal_coherence > 0.4:
                rationale_parts.append("coerência parcial entre goal e texto")
            else:
                rationale_parts.append("baixa coerência entre goal e texto")
        
        if redundancy_score > 0.5:
            rationale_parts.append("alta redundância detectada")
        elif redundancy_score < 0.3:
            rationale_parts.append("baixa redundância")
        
        rationale = ". ".join(rationale_parts) if rationale_parts else "Análise semiótica básica"
        
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
    
    def _calculate_goal_coherence(self, text: str, goal: str) -> float:
        """
        Calcula coerência entre goal e texto
        
        Args:
            text: Texto da peça
            goal: Goal da peça (ex: "whatsapp_click")
        
        Returns:
            Score de coerência (0-1)
        """
        if not goal or not text:
            return 0.5  # Neutro se não há goal ou texto
        
        # Mapeamento de goals para keywords esperadas
        goal_keywords = {
            "whatsapp_click": ["whatsapp", "chame", "fale", "contato", "zap"],
            "link_click": ["link", "acesse", "saiba mais", "confira"],
            "purchase": ["compre", "garanta", "adquira", "peça"],
            "download": ["baixe", "download", "instale"],
            "signup": ["cadastre", "inscreva", "registre"]
        }
        
        expected_keywords = goal_keywords.get(goal, [])
        if not expected_keywords:
            return 0.5  # Goal desconhecido
        
        # Verificar se keywords esperadas aparecem no texto
        matches = self.detect_keywords(text, expected_keywords)
        coherence = min(matches / len(expected_keywords), 1.0)
        
        return coherence
    
    def _calculate_redundancy(self, text: str) -> float:
        """
        Calcula score de redundância (0-1, onde 1 = muito redundante)
        
        Args:
            text: Texto a analisar
        
        Returns:
            Score de redundância
        """
        if not text:
            return 0.0
        
        words = text.split()
        if len(words) == 0:
            return 0.0
        
        # Contar palavras únicas vs total
        unique_words = len(set(words))
        total_words = len(words)
        
        # Redundância = 1 - (únicas / total)
        # Se todas palavras são únicas: redundância = 0
        # Se todas palavras são repetidas: redundância tende a 1
        redundancy = 1.0 - (unique_words / total_words)
        
        return redundancy
    
    def _calculate_score(
        self, 
        cta_detected: bool, 
        goal_coherence: float, 
        redundancy_score: float
    ) -> float:
        """
        Calcula score final (0-100)
        
        Heurística:
        - Base: 50
        - +20 se CTA detectado
        - +20 * goal_coherence
        - -15 * redundancy_score
        """
        score = 50.0
        
        if cta_detected:
            score += 20.0
        
        score += 20.0 * goal_coherence
        score -= 15.0 * redundancy_score
        
        return score
    
    def _calculate_confidence(
        self, 
        cta_detected: bool, 
        goal_coherence: float, 
        cta_keywords_found: int
    ) -> float:
        """
        Calcula confidence (0-1)
        
        Base: 0.55
        Sobe se houver mais sinais (CTA + goal match + múltiplas keywords)
        """
        confidence = 0.55
        
        if cta_detected:
            confidence += 0.10
        
        if goal_coherence > 0.7:
            confidence += 0.10
        
        if cta_keywords_found > 1:
            confidence += 0.05
        
        return confidence


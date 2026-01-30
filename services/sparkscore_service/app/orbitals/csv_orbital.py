"""
Orbital Circulação Simbólica Vetorial (CSV)
Analisa fluxo vetorial dos símbolos: direção, propagação, adequação ao canal.
"""

from typing import Dict, List
from app.orbitals.base_orbital import BaseOrbital
from app.orbitals.orbital_result import OrbitalResult


class CsvOrbital(BaseOrbital):
    """
    Orbital Circulação Simbólica Vetorial (CSV) - Analisa:
    - Direção do vetor (emissor → receptor, objetivo + CTA)
    - Gatilhos de circulação (hashtags, compartilhe, envie, marque)
    - Adequação do formato ao canal
    - Obstáculos à circulação (texto longo, ambiguidade)
    """

    def __init__(self):
        super().__init__(
            orbital_id="csv",
            name="Orbital Circulação Simbólica Vetorial (CSV)",
            version="1.0.0"
        )

        # Gatilhos de circulação
        self.circulation_keywords = [
            "compartilhe", "envie", "marque", "repasse", "encaminhe",
            "chame", "convide", "indique", "divulga", "whatsapp",
            "fale", "contato", "zap"
        ]

    def analyze(self, payload: Dict) -> OrbitalResult:
        """
        Analisa payload do ponto de vista da circulação simbólica vetorial
        """
        text = self.extract_text_content(payload)
        goal = self.extract_goal(payload)
        context = self.extract_context(payload)
        piece = payload.get("piece", {})
        distribution = payload.get("distribution", {})
        hashtags = piece.get("hashtags", [])

        # Features brutas
        raw_features = {}

        # 1. Hashtags
        hashtag_count = len(hashtags) if isinstance(hashtags, list) else 0
        if hashtag_count == 0 and text:
            hashtag_count = self._count_hashtags_in_text(text)
        raw_features["hashtag_count"] = hashtag_count

        # 2. Gatilhos de circulação
        circulation_triggers = self.detect_keywords(text, self.circulation_keywords)
        circulation_triggers += hashtag_count
        raw_features["circulation_triggers_found"] = circulation_triggers

        # 3. Convite explícito a compartilhar
        share_keywords = ["compartilhe", "envie", "marque", "repasse", "encaminhe", "divulga"]
        share_invitation = self.detect_keywords(text, share_keywords) > 0
        raw_features["share_invitation_detected"] = share_invitation

        # 4. Clareza do vetor (objetivo + CTA)
        vector_clarity = self._calculate_vector_clarity(text, goal)
        raw_features["vector_clarity"] = vector_clarity

        # 5. Adequação formato-canal
        channel_fit = self._calculate_channel_circulation_fit(distribution)
        raw_features["channel_circulation_fit"] = channel_fit

        # 6. Obstáculos à circulação
        obstacle_score = self._calculate_obstacle_score(text)
        raw_features["obstacle_score"] = obstacle_score

        # 7. Calcular score
        score = self._calculate_score(
            share_invitation, circulation_triggers, vector_clarity, channel_fit, obstacle_score
        )
        score = self.clamp_score(score)

        # 8. Calcular confidence
        confidence = self._calculate_confidence(
            hashtag_count, circulation_triggers, goal, channel_fit
        )
        confidence = self.clamp_confidence(confidence)

        # 9. Top features
        top_features = []
        if circulation_triggers > 0:
            top_features.append("circulation_triggers_detected")
        if vector_clarity > 0.7:
            top_features.append("high_vector_clarity")
        elif vector_clarity > 0.4:
            top_features.append("moderate_vector_clarity")
        if channel_fit > 0.7:
            top_features.append("good_channel_fit")
        if obstacle_score < 0.3:
            top_features.append("low_obstacle")

        # 10. Rationale
        rationale = self._build_rationale(
            vector_clarity, circulation_triggers, channel_fit, obstacle_score
        )

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

    def _count_hashtags_in_text(self, text: str) -> int:
        """Conta hashtags no texto (#palavra)"""
        if not text:
            return 0
        words = text.split()
        return sum(1 for w in words if w.startswith("#"))

    def _calculate_vector_clarity(self, text: str, goal: str) -> float:
        """
        Clareza da direção do vetor: objetivo + CTA presente
        Retorna 0-1
        """
        if not text:
            return 0.3

        score = 0.5
        cta_keywords = ["chame", "clique", "whatsapp", "fale", "contato", "acesse", "veja"]
        cta_found = self.detect_keywords(text, cta_keywords) > 0
        if cta_found:
            score += 0.25
        goal_parts = goal.replace("_", " ").split() if goal else []
        if goal_parts and self.detect_keywords(text, goal_parts) > 0:
            score += 0.2
        if len(text.split()) >= 3:
            score += 0.1

        return min(score, 1.0)

    def _calculate_channel_circulation_fit(self, distribution: Dict) -> float:
        """
        Adequação do formato ao canal de circulação
        story_vertical + whatsapp_status = bom fit
        """
        channel = distribution.get("channel", "").lower()
        format_type = distribution.get("format", "").lower()

        if not channel and not format_type:
            return 0.6

        fit = 0.6
        if "whatsapp" in channel or "status" in channel:
            fit += 0.2
        if "story" in format_type or "vertical" in format_type:
            fit += 0.2
        if "instagram" in channel or "feed" in channel:
            fit += 0.1

        return min(fit, 1.0)

    def _calculate_obstacle_score(self, text: str) -> float:
        """
        Obstáculos à circulação: texto muito longo, redundância
        Retorna 0-1 (1 = muitos obstáculos)
        """
        if not text:
            return 0.0

        words = text.split()
        word_count = len(words)

        obstacle = 0.0
        if word_count > 50:
            obstacle += 0.5
        elif word_count > 30:
            obstacle += 0.3
        elif word_count > 15:
            obstacle += 0.1

        unique_ratio = len(set(words)) / max(word_count, 1)
        if unique_ratio < 0.5:
            obstacle += 0.3
        elif unique_ratio < 0.7:
            obstacle += 0.1

        return min(obstacle, 1.0)

    def _calculate_score(
        self,
        share_invitation: bool,
        circulation_triggers: int,
        vector_clarity: float,
        channel_fit: float,
        obstacle_score: float
    ) -> float:
        """
        Score final (0-100)
        Base: 60
        +10 share_invitation, +5*triggers (máx 15), +15*clarity, +10*fit, -20*obstacle
        """
        score = 60.0
        if share_invitation:
            score += 10.0
        score += min(circulation_triggers * 5, 15.0)
        score += 15.0 * vector_clarity
        score += 10.0 * channel_fit
        score -= 20.0 * obstacle_score
        return score

    def _calculate_confidence(
        self,
        hashtag_count: int,
        circulation_triggers: int,
        goal: str,
        channel_fit: float
    ) -> float:
        """Confidence 0-1"""
        confidence = 0.5
        if hashtag_count > 0:
            confidence += 0.05
        if circulation_triggers > 1:
            confidence += 0.05
        if goal:
            confidence += 0.05
        if channel_fit > 0.7:
            confidence += 0.05
        return confidence

    def _build_rationale(
        self,
        vector_clarity: float,
        circulation_triggers: int,
        channel_fit: float,
        obstacle_score: float
    ) -> str:
        """Monta rationale descritivo"""
        parts = []

        if vector_clarity > 0.7:
            parts.append("Vetor com direção clara")
        elif vector_clarity > 0.4:
            parts.append("Vetor com direção moderada")
        else:
            parts.append("Vetor com direção fraca")

        if circulation_triggers > 0:
            parts.append(f"{circulation_triggers} gatilhos de circulação (hashtags, keywords)")
        else:
            parts.append("nenhum gatilho de circulação detectado")

        if channel_fit > 0.7:
            parts.append("bom ajuste ao formato/canal")
        elif channel_fit > 0.5:
            parts.append("ajuste moderado ao formato/canal")

        if obstacle_score < 0.3:
            parts.append("baixo obstáculo à circulação")
        elif obstacle_score > 0.5:
            parts.append("obstáculos à circulação detectados")

        return ". ".join(parts) if parts else "Análise CSV básica"

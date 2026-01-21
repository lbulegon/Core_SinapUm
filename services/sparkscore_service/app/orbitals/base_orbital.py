"""
Classe base para todos os orbitais
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from app.orbitals.orbital_result import OrbitalResult


class BaseOrbital(ABC):
    """
    Classe base para orbitais
    """
    
    def __init__(self, orbital_id: str, name: str, version: str = "1.0.0"):
        self.orbital_id = orbital_id
        self.name = name
        self.version = version
    
    @abstractmethod
    def analyze(self, payload: Dict) -> OrbitalResult:
        """
        Analisa payload e retorna resultado orbital
        
        Args:
            payload: Payload da peça do Creative Engine
                - text_overlay: str (opcional)
                - caption: str (opcional)
                - goal: str (opcional, ex: "whatsapp_click")
                - context: dict (opcional, ex: {"channel": "...", "format": "..."})
        
        Returns:
            OrbitalResult com análise completa
        """
        pass
    
    def clamp_score(self, score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """
        Limita score entre min e max
        
        Args:
            score: Score a limitar
            min_val: Valor mínimo (padrão: 0.0)
            max_val: Valor máximo (padrão: 100.0)
        
        Returns:
            Score limitado
        """
        return max(min_val, min(max_val, score))
    
    def clamp_confidence(self, confidence: float) -> float:
        """
        Limita confidence entre 0.0 e 1.0
        
        Args:
            confidence: Confidence a limitar
        
        Returns:
            Confidence limitado
        """
        return max(0.0, min(1.0, confidence))
    
    def normalize_text(self, text: Optional[str]) -> str:
        """
        Normaliza texto para análise (lowercase, strip)
        
        Args:
            text: Texto a normalizar
        
        Returns:
            Texto normalizado ou string vazia
        """
        if not text:
            return ""
        return text.lower().strip()
    
    def extract_text_content(self, payload: Dict) -> str:
        """
        Extrai todo o conteúdo textual do payload
        Suporta tanto payload antigo quanto payload padrão do Creative Engine
        
        Args:
            payload: Payload da peça (pode ser formato antigo ou Creative Engine)
        
        Returns:
            Texto combinado (text_overlay + caption)
        """
        # Tentar formato Creative Engine primeiro (piece.text_overlay, piece.caption)
        piece = payload.get("piece", {})
        if piece:
            text_overlay = self.normalize_text(piece.get("text_overlay"))
            caption = self.normalize_text(piece.get("caption"))
        else:
            # Fallback para formato antigo (text_overlay, caption direto)
            text_overlay = self.normalize_text(payload.get("text_overlay"))
            caption = self.normalize_text(payload.get("caption"))
        
        parts = [text_overlay, caption]
        return " ".join([p for p in parts if p])
    
    def extract_goal(self, payload: Dict) -> str:
        """
        Extrai goal do payload (suporta ambos formatos)
        
        Args:
            payload: Payload da peça
        
        Returns:
            Goal como string (ex: "whatsapp_click")
        """
        # Tentar formato Creative Engine primeiro
        objective = payload.get("objective", {})
        if objective:
            goal = objective.get("primary_goal", "")
            if goal:
                return goal.lower()
        
        # Fallback para formato antigo
        goal = payload.get("goal", "")
        return goal.lower() if goal else ""
    
    def extract_context(self, payload: Dict) -> Dict:
        """
        Extrai contexto do payload (suporta ambos formatos)
        
        Args:
            payload: Payload da peça
        
        Returns:
            Dict com contexto (channel, format, etc)
        """
        # Tentar formato Creative Engine primeiro
        distribution = payload.get("distribution", {})
        if distribution:
            return {
                "channel": distribution.get("channel", ""),
                "format": distribution.get("format", "")
            }
        
        # Fallback para formato antigo
        context = payload.get("context", {})
        return {
            "channel": context.get("channel", ""),
            "format": context.get("format", "")
        }
    
    def count_words(self, text: str) -> int:
        """
        Conta palavras em texto
        
        Args:
            text: Texto a contar
        
        Returns:
            Número de palavras
        """
        if not text:
            return 0
        return len(text.split())
    
    def detect_keywords(self, text: str, keywords: List[str]) -> int:
        """
        Detecta quantas keywords aparecem no texto
        
        Args:
            text: Texto a analisar
            keywords: Lista de keywords
        
        Returns:
            Número de keywords encontradas
        """
        if not text or not keywords:
            return 0
        
        text_lower = text.lower()
        return sum(1 for kw in keywords if kw in text_lower)


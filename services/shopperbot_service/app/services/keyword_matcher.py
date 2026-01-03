"""Utilitário para matching de palavras-chave"""
from typing import List


class KeywordMatcher:
    """Faz matching de palavras-chave em mensagens"""
    
    def match_score(self, text: str, keywords: List[str]) -> float:
        """
        Retorna score de matching (0.0 a 1.0)
        Score baseado em quantas palavras-chave aparecem e sua frequência
        """
        if not keywords:
            return 0.0
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in text:
                matches += 1
        
        # Score proporcional ao número de matches
        score = matches / len(keywords)
        
        # Boost se houver múltiplas matches
        if matches > 1:
            score = min(1.0, score * 1.5)
        
        return score


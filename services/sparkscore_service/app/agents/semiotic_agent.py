"""
Agente Semiótico - Análise baseada em Peirce, categorias e efeito Mandela
"""

from typing import Dict, Optional


class SemioticAgent:
    """
    Agente especializado em análise semiótica
    - Teoria de Peirce (ícone, índice, símbolo)
    - Categorias semióticas
    - Efeito Mandela (memória coletiva induzida)
    """
    
    def analyze(
        self,
        stimulus: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Analisa estímulo do ponto de vista semiótico
        
        Returns:
            Dict com análise semiótica
        """
        text = stimulus.get('text', '').lower()
        
        # Análise de Peirce
        peirce_analysis = self._analyze_peirce(stimulus)
        
        # Categorias semióticas
        categories = self._extract_categories(text)
        
        # Efeito Mandela (memória coletiva)
        mandela_effect = self._detect_mandela_effect(text, context)
        
        # Coerência simbólica
        coherence = self._calculate_coherence(text, peirce_analysis)
        
        return {
            'peirce_type': peirce_analysis['type'],
            'peirce_confidence': peirce_analysis['confidence'],
            'categories': categories,
            'mandela_effect': mandela_effect,
            'coherence_score': coherence,
            'semiotic_analysis': {
                'icon_score': peirce_analysis.get('icon_score', 0.0),
                'index_score': peirce_analysis.get('index_score', 0.0),
                'symbol_score': peirce_analysis.get('symbol_score', 0.0)
            }
        }
    
    def _analyze_peirce(self, stimulus: Dict) -> Dict:
        """Analisa tipo semiótico de Peirce"""
        text = stimulus.get('text', '').lower()
        has_image = 'image' in stimulus or 'image_url' in stimulus
        
        scores = {
            'icon': 0.0,
            'index': 0.0,
            'symbol': 0.0
        }
        
        # Ícone (similaridade visual)
        if has_image:
            scores['icon'] = 0.8
        
        icon_keywords = ['imagem', 'visual', 'foto', 'desenho', 'ilustração']
        if any(kw in text for kw in icon_keywords):
            scores['icon'] += 0.2
        
        # Índice (causalidade, referência)
        index_keywords = ['causa', 'efeito', 'sinal', 'indicador', 'referência', 'aponta']
        index_matches = sum(1 for kw in index_keywords if kw in text)
        scores['index'] = min(index_matches / len(index_keywords), 1.0)
        
        # Símbolo (convenção, linguagem)
        symbol_keywords = ['palavra', 'texto', 'marca', 'nome', 'conceito', 'significado']
        symbol_matches = sum(1 for kw in symbol_keywords if kw in text)
        scores['symbol'] = min(symbol_matches / len(symbol_keywords), 1.0)
        
        # Se não tem imagem e pouco texto, assume símbolo
        if not has_image and len(text) < 10:
            scores['symbol'] = max(scores['symbol'], 0.5)
        
        # Determinar tipo dominante
        dominant_type = max(scores, key=scores.get)
        confidence = scores[dominant_type]
        
        return {
            'type': dominant_type,
            'confidence': confidence,
            'icon_score': scores['icon'],
            'index_score': scores['index'],
            'symbol_score': scores['symbol']
        }
    
    def _extract_categories(self, text: str) -> list:
        """Extrai categorias semióticas do texto"""
        categories = []
        
        category_keywords = {
            'temporal': ['tempo', 'agora', 'futuro', 'passado', 'momento'],
            'spatial': ['lugar', 'local', 'aqui', 'lá', 'espaço'],
            'modal': ['pode', 'deve', 'precisa', 'possível', 'necessário'],
            'emotional': ['sentimento', 'emoção', 'amor', 'medo', 'alegria']
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in text for kw in keywords):
                categories.append(category)
        
        return categories
    
    def _detect_mandela_effect(self, text: str, context: Optional[Dict]) -> Dict:
        """
        Detecta potencial de efeito Mandela
        Memória coletiva induzida por consenso simbólico
        """
        mandela_keywords = [
            'sempre', 'todo mundo', 'todos', 'coletivo', 'comunidade',
            'lembro', 'lembramos', 'todos sabem', 'consenso'
        ]
        
        matches = sum(1 for kw in mandela_keywords if kw in text)
        mandela_score = min(matches / len(mandela_keywords), 1.0)
        
        # Verificar recorrência no contexto
        recurrence = 0.0
        if context:
            exposure_count = context.get('exposure_count', 0)
            recurrence = min(exposure_count / 10.0, 1.0)
        
        return {
            'detected': mandela_score > 0.3,
            'score': mandela_score,
            'recurrence': recurrence,
            'potential': (mandela_score + recurrence) / 2.0
        }
    
    def _calculate_coherence(self, text: str, peirce_analysis: Dict) -> float:
        """Calcula coerência simbólica"""
        # Coerência baseada na consistência do tipo de Peirce
        peirce_confidence = peirce_analysis['confidence']
        
        # Coerência baseada em padrões repetidos
        words = text.split()
        if len(words) > 0:
            unique_ratio = len(set(words)) / len(words)
            pattern_coherence = 1.0 - unique_ratio  # Mais repetição = mais coerência
        else:
            pattern_coherence = 0.0
        
        # Média ponderada
        coherence = (peirce_confidence * 0.6) + (pattern_coherence * 0.4)
        
        return min(coherence, 1.0)


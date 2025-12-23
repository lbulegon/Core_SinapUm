"""
Classificador Orbital - Determina em qual Orbital Cognitivo um estímulo atua
Baseado na arquitetura orbital do SparkScore
"""

import yaml
from typing import Dict, List, Optional
from pathlib import Path
from app.core.semiotic_normalizer import SemioticNormalizer


class OrbitalClassifier:
    """
    Classifica estímulos em Orbitais Cognitivos (0-6)
    
    Orbitais:
    0 - Ruído (não integrado)
    1 - Reconhecimento (familiaridade)
    2 - Expectativa (antecipação / PPA)
    3 - Alinhamento (coerência simbólica)
    4 - Engajamento (decisão / ação)
    5 - Memória (retenção)
    6 - Efeito Mandela (memória coletiva induzida)
    """
    
    def __init__(self):
        self.orbitals_config = self._load_orbitals()
        self.normalizer = SemioticNormalizer()
    
    def _load_orbitals(self) -> Dict:
        """Carrega configuração dos orbitais"""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'orbitals.yaml'
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def classify(
        self, 
        stimulus: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Classifica estímulo em orbital dominante e secundários
        
        Args:
            stimulus: Estímulo a ser classificado (texto, imagem, marca, etc.)
            context: Contexto adicional (usuário, histórico, etc.)
        
        Returns:
            Dict com orbital_dominante, orbitais_secundarios, justificativa, etc.
        """
        # Normalizar estímulo semioticamente
        normalized = self.normalizer.normalize(stimulus, context)
        
        # Extrair sinais para classificação
        signals = self._extract_signals(normalized, context)
        
        # Calcular scores por orbital
        orbital_scores = self._calculate_orbital_scores(signals)
        
        # Determinar orbital dominante
        dominant_orbital = max(orbital_scores, key=orbital_scores.get)
        
        # Determinar orbitais secundários (score > 0.3)
        secondary_orbitals = [
            orb_id for orb_id, score in orbital_scores.items()
            if score > 0.3 and orb_id != dominant_orbital
        ]
        
        # Calcular grau de estabilidade
        stability = self._calculate_stability(orbital_scores, dominant_orbital)
        
        # Gerar justificativa
        justification = self._generate_justification(
            dominant_orbital, 
            signals, 
            orbital_scores
        )
        
        # Calcular impacto no SparkScore (0.0-1.0)
        impact = self._calculate_impact(dominant_orbital, orbital_scores)
        
        return {
            'orbital_dominante': dominant_orbital,
            'orbitais_secundarios': secondary_orbitals,
            'grau_de_estabilidade': stability,
            'justificativa': justification,
            'impacto_no_sparkscore': impact,
            'scores_por_orbital': orbital_scores,
            'sinais_detectados': signals
        }
    
    def _extract_signals(self, normalized: Dict, context: Optional[Dict]) -> Dict:
        """Extrai sinais para classificação orbital"""
        signals = {
            'familiaridade_percebida': 0.0,
            'coerencia_simbolica': 0.0,
            'antecipacao_ppa': 0.0,
            'intensidade_emocional': 0.0,
            'recorrencia_coletiva': 0.0,
            'tempo_exposicao': 0.0
        }
        
        # Analisar texto se presente
        text = normalized.get('text', '').lower()
        
        # Familiaridade percebida
        familiar_keywords = ['já vi', 'conheço', 'familiar', 'reconheço', 'lembro']
        signals['familiaridade_percebida'] = min(
            sum(1 for kw in familiar_keywords if kw in text) / len(familiar_keywords),
            1.0
        )
        
        # Coerência simbólica (padrões consistentes)
        coherent_patterns = ['marca', 'identidade', 'consistente', 'alinhado']
        signals['coerencia_simbolica'] = min(
            sum(1 for pattern in coherent_patterns if pattern in text) / len(coherent_patterns),
            1.0
        )
        
        # Antecipação PPA
        ppa_keywords = ['espero', 'quero', 'preciso', 'vou', 'futuro', 'próximo']
        signals['antecipacao_ppa'] = min(
            sum(1 for kw in ppa_keywords if kw in text) / len(ppa_keywords),
            1.0
        )
        
        # Intensidade emocional
        emotional_keywords = ['amor', 'ódio', 'medo', 'alegria', 'tristeza', 'raiva', 'paixão']
        signals['intensidade_emocional'] = min(
            sum(1 for kw in emotional_keywords if kw in text) / len(emotional_keywords),
            1.0
        )
        
        # Recorrência coletiva (efeito Mandela)
        collective_keywords = ['sempre', 'todo mundo', 'todos', 'coletivo', 'comunidade']
        signals['recorrencia_coletiva'] = min(
            sum(1 for kw in collective_keywords if kw in text) / len(collective_keywords),
            1.0
        )
        
        # Tempo de exposição (do contexto)
        if context:
            exposure_time = context.get('exposure_time', 0)
            signals['tempo_exposicao'] = min(exposure_time / 60.0, 1.0)  # Normalizar para 60s
        
        return signals
    
    def _calculate_orbital_scores(self, signals: Dict) -> Dict[int, float]:
        """Calcula score para cada orbital baseado nos sinais"""
        scores = {}
        
        # Orbital 0 - Ruído (baixa familiaridade, baixa coerência)
        scores[0] = (1 - signals['familiaridade_percebida']) * (1 - signals['coerencia_simbolica'])
        
        # Orbital 1 - Reconhecimento (alta familiaridade)
        scores[1] = signals['familiaridade_percebida'] * (1 - signals['antecipacao_ppa'])
        
        # Orbital 2 - Expectativa (alta antecipação PPA)
        scores[2] = signals['antecipacao_ppa'] * signals['familiaridade_percebida']
        
        # Orbital 3 - Alinhamento (alta coerência simbólica)
        scores[3] = signals['coerencia_simbolica'] * (1 - signals['intensidade_emocional'])
        
        # Orbital 4 - Engajamento (alta intensidade emocional + coerência)
        scores[4] = signals['intensidade_emocional'] * signals['coerencia_simbolica']
        
        # Orbital 5 - Memória (alta familiaridade + tempo de exposição)
        scores[5] = signals['familiaridade_percebida'] * signals['tempo_exposicao']
        
        # Orbital 6 - Efeito Mandela (alta recorrência coletiva + familiaridade)
        scores[6] = signals['recorrencia_coletiva'] * signals['familiaridade_percebida']
        
        return scores
    
    def _calculate_stability(self, scores: Dict[int, float], dominant: int) -> float:
        """Calcula grau de estabilidade (quanto mais concentrado, mais estável)"""
        dominant_score = scores[dominant]
        total_score = sum(scores.values())
        
        if total_score == 0:
            return 0.0
        
        # Estabilidade = proporção do score dominante
        stability = dominant_score / total_score
        
        return min(stability, 1.0)
    
    def _generate_justification(
        self, 
        dominant: int, 
        signals: Dict, 
        scores: Dict[int, float]
    ) -> str:
        """Gera justificativa para classificação orbital"""
        orbital_names = {
            0: "Ruído",
            1: "Reconhecimento",
            2: "Expectativa",
            3: "Alinhamento",
            4: "Engajamento",
            5: "Memória",
            6: "Efeito Mandela"
        }
        
        name = orbital_names.get(dominant, "Desconhecido")
        score = scores[dominant]
        
        # Justificativa baseada nos sinais mais relevantes
        top_signals = sorted(
            signals.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:2]
        
        signal_names = {
            'familiaridade_percebida': 'familiaridade',
            'coerencia_simbolica': 'coerência simbólica',
            'antecipacao_ppa': 'antecipação PPA',
            'intensidade_emocional': 'intensidade emocional',
            'recorrencia_coletiva': 'recorrência coletiva',
            'tempo_exposicao': 'tempo de exposição'
        }
        
        signal_desc = ', '.join([
            f"{signal_names.get(sig, sig)} ({val:.2f})" 
            for sig, val in top_signals
        ])
        
        return (
            f"Orbital {dominant} ({name}) com score {score:.2f}. "
            f"Sinais principais: {signal_desc}"
        )
    
    def _calculate_impact(self, dominant: int, scores: Dict[int, float]) -> float:
        """Calcula impacto no SparkScore (0.0-1.0)"""
        # Orbitais mais altos têm mais impacto
        # Orbital 0 (ruído) = baixo impacto
        # Orbitais 4-6 = alto impacto
        
        impact_weights = {
            0: 0.1,  # Ruído - baixo impacto
            1: 0.3,  # Reconhecimento - médio
            2: 0.5,  # Expectativa - médio-alto (PPA nasce)
            3: 0.7,  # Alinhamento - alto (confiança)
            4: 0.9,  # Engajamento - muito alto (decisão)
            5: 0.6,  # Memória - médio-alto (retenção)
            6: 0.95  # Efeito Mandela - máximo (narrativa coletiva)
        }
        
        weight = impact_weights.get(dominant, 0.5)
        score = scores[dominant]
        
        return weight * score


def classify_orbital(stimulus: Dict, context: Optional[Dict] = None) -> Dict:
    """
    Função helper para classificar orbital
    """
    classifier = OrbitalClassifier()
    return classifier.classify(stimulus, context)


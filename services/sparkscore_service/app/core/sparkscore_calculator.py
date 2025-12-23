"""
Calculadora do SparkScore Final
Combina análise orbital com agentes especializados
"""

from typing import Dict, Optional, List
from app.core.orbital_classifier import OrbitalClassifier
from app.agents.semiotic_agent import SemioticAgent
from app.agents.psycho_agent import PsychoAgent
from app.agents.metric_agent import MetricAgent
from app.motors.orbital_motor_factory import OrbitalMotorFactory


class SparkScoreCalculator:
    """
    Calcula SparkScore final combinando:
    - Classificação Orbital
    - Agente Semiótico (Peirce, categorias, efeito Mandela)
    - Agente Psico (atração, risco, ruído)
    - Agente Métrico (probabilidade de engajamento/conversão)
    """
    
    def __init__(self):
        self.orbital_classifier = OrbitalClassifier()
        self.semiotic_agent = SemioticAgent()
        self.psycho_agent = PsychoAgent()
        self.metric_agent = MetricAgent()
        self.motor_factory = OrbitalMotorFactory()
    
    def calculate(
        self,
        stimulus: Dict,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Calcula SparkScore completo
        
        Args:
            stimulus: Estímulo a analisar
            context: Contexto adicional
        
        Returns:
            Dict com SparkScore completo e PPA
        """
        # 1. Classificação Orbital
        orbital_result = self.orbital_classifier.classify(stimulus, context)
        dominant_orbital = orbital_result['orbital_dominante']
        
        # 2. Análise Semiótica
        semiotic_result = self.semiotic_agent.analyze(stimulus, context)
        
        # 3. Análise Psicológica
        psycho_result = self.psycho_agent.analyze(stimulus, context)
        
        # 4. Análise Métrica
        metric_result = self.metric_agent.analyze(stimulus, context)
        
        # 5. Executar motor do orbital dominante
        motor = self.motor_factory.get_motor(dominant_orbital)
        motor_result = motor.process(stimulus, orbital_result, context)
        
        # 6. Calcular SparkScore final
        sparkscore = self._combine_scores(
            orbital_result,
            semiotic_result,
            psycho_result,
            metric_result,
            motor_result
        )
        
        # 7. Calcular PPA (Perfil Psicológico de Atendimento)
        ppa = self._calculate_ppa(
            dominant_orbital,
            psycho_result,
            orbital_result
        )
        
        return {
            'sparkscore': sparkscore,
            'ppa': ppa,
            'orbital': orbital_result,
            'semiotic': semiotic_result,
            'psycho': psycho_result,
            'metric': metric_result,
            'motor_result': motor_result,
            'recommendations': self._generate_recommendations(
                sparkscore,
                dominant_orbital,
                ppa
            )
        }
    
    def _combine_scores(
        self,
        orbital: Dict,
        semiotic: Dict,
        psycho: Dict,
        metric: Dict,
        motor: Dict
    ) -> float:
        """
        Combina todos os scores em SparkScore final (0.0-1.0)
        """
        # Pesos para cada componente
        weights = {
            'orbital': 0.3,      # Classificação orbital
            'semiotic': 0.2,      # Análise semiótica
            'psycho': 0.25,       # Análise psicológica
            'metric': 0.15,       # Métricas de engajamento
            'motor': 0.1         # Resultado do motor
        }
        
        # Extrair scores
        orbital_score = orbital.get('impacto_no_sparkscore', 0.0)
        semiotic_score = semiotic.get('coherence_score', 0.0)
        psycho_score = psycho.get('attraction_score', 0.0)
        metric_score = metric.get('engagement_probability', 0.0)
        motor_score = motor.get('processing_score', 0.0)
        
        # Calcular média ponderada
        sparkscore = (
            weights['orbital'] * orbital_score +
            weights['semiotic'] * semiotic_score +
            weights['psycho'] * psycho_score +
            weights['metric'] * metric_score +
            weights['motor'] * motor_score
        )
        
        return min(max(sparkscore, 0.0), 1.0)
    
    def _calculate_ppa(
        self,
        dominant_orbital: int,
        psycho_result: Dict,
        orbital_result: Dict
    ) -> Dict:
        """
        Calcula PPA (Perfil Psicológico de Atendimento)
        PPA nasce no Orbital 2, validado no 3, ativado no 4, cristalizado no 6
        """
        ppa = {
            'status': 'inativo',
            'stage': None,
            'confidence': 0.0,
            'profile': {}
        }
        
        # Determinar estágio do PPA baseado no orbital
        if dominant_orbital == 2:
            ppa['status'] = 'nascente'
            ppa['stage'] = 'nasce'
            ppa['confidence'] = orbital_result.get('impacto_no_sparkscore', 0.0) * 0.5
        elif dominant_orbital == 3:
            ppa['status'] = 'validado'
            ppa['stage'] = 'validado'
            ppa['confidence'] = orbital_result.get('impacto_no_sparkscore', 0.0) * 0.7
        elif dominant_orbital == 4:
            ppa['status'] = 'ativo'
            ppa['stage'] = 'ativado'
            ppa['confidence'] = orbital_result.get('impacto_no_sparkscore', 0.0) * 0.9
        elif dominant_orbital == 6:
            ppa['status'] = 'cristalizado'
            ppa['stage'] = 'cristalizado'
            ppa['confidence'] = orbital_result.get('impacto_no_sparkscore', 0.0)
        else:
            ppa['status'] = 'inativo'
            ppa['confidence'] = 0.0
        
        # Perfil psicológico
        ppa['profile'] = {
            'attraction': psycho_result.get('attraction_score', 0.0),
            'risk': psycho_result.get('risk_score', 0.0),
            'noise': psycho_result.get('noise_score', 0.0),
            'emotional_intensity': psycho_result.get('emotional_intensity', 0.0)
        }
        
        return ppa
    
    def _generate_recommendations(
        self,
        sparkscore: float,
        dominant_orbital: int,
        ppa: Dict
    ) -> List[str]:
        """Gera recomendações baseadas no SparkScore"""
        recommendations = []
        
        if sparkscore < 0.3:
            recommendations.append("SparkScore baixo - considerar ajustar estímulo")
        
        if dominant_orbital == 0:
            recommendations.append("Estímulo em ruído - melhorar familiaridade e coerência")
        
        if dominant_orbital == 2 and ppa['status'] == 'nascente':
            recommendations.append("PPA nascente - potencial para desenvolvimento")
        
        if dominant_orbital == 4:
            recommendations.append("Alto engajamento - momento ideal para call-to-action")
        
        if ppa['profile']['risk'] > 0.7:
            recommendations.append("Alto risco percebido - considerar mitigação")
        
        if sparkscore > 0.8:
            recommendations.append("SparkScore excelente - manter estratégia")
        
        return recommendations


def calculate_sparkscore(stimulus: Dict, context: Optional[Dict] = None) -> Dict:
    """
    Função helper para calcular SparkScore
    """
    calculator = SparkScoreCalculator()
    return calculator.calculate(stimulus, context)


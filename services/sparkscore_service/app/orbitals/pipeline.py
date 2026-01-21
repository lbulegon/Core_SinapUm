"""
Pipeline Orbital - Executa análise completa de orbitais
"""

from typing import Dict, List
from app.orbitals.registry import OrbitalRegistry
from app.orbitals.orbital_result import OrbitalResult


class OrbitalPipeline:
    """
    Pipeline que executa todos os orbitais e gera análise completa
    """
    
    def __init__(self):
        self.registry = OrbitalRegistry()
        self.pipeline_version = "1.0.0"
    
    def run_orbitals(self, payload: Dict) -> Dict:
        """
        Executa todos os orbitais (ativos + placeholders) e gera análise completa
        
        Args:
            payload: Payload da peça do Creative Engine
            
        Returns:
            Dict com análise completa:
            {
                "pipeline_version": str,
                "overall_score": float,
                "orbitals": [OrbitalResult...],
                "insights": List[Dict]
            }
        """
        # 1. Executar orbitais ativos
        active_orbitals = self.registry.get_active_orbitals()
        active_results = []
        
        for orbital in active_orbitals:
            try:
                result = orbital.analyze(payload)
                active_results.append(result)
            except Exception as e:
                # Em caso de erro, criar resultado de erro
                error_result = OrbitalResult(
                    orbital_id=orbital.orbital_id,
                    name=orbital.name,
                    status="disabled",
                    score=None,
                    confidence=None,
                    rationale=f"Erro ao processar orbital: {str(e)}",
                    top_features=[],
                    raw_features={"error": str(e)},
                    version=orbital.version
                )
                active_results.append(error_result)
        
        # 2. Incluir placeholders
        placeholder_orbitals = self.registry.get_placeholder_orbitals()
        placeholder_results = []
        
        for orbital in placeholder_orbitals:
            try:
                result = orbital.analyze(payload)
                placeholder_results.append(result)
            except Exception as e:
                # Em caso de erro, criar resultado de erro
                error_result = OrbitalResult(
                    orbital_id=orbital.orbital_id,
                    name=orbital.name,
                    status="disabled",
                    score=None,
                    confidence=None,
                    rationale=f"Erro ao processar orbital: {str(e)}",
                    top_features=[],
                    raw_features={"error": str(e)},
                    version=orbital.version
                )
                placeholder_results.append(error_result)
        
        # 3. Combinar resultados (ativos primeiro, depois placeholders)
        all_results = active_results + placeholder_results
        
        # 4. Calcular overall_score (média ponderada dos orbitais ativos)
        overall_score = self._calculate_overall_score(active_results)
        
        # 5. Gerar insights
        insights = self._generate_insights(payload, active_results)
        
        return {
            "pipeline_version": self.pipeline_version,
            "overall_score": overall_score,
            "orbitals": [result.model_dump() for result in all_results],
            "insights": insights
        }
    
    def _calculate_overall_score(self, active_results: List[OrbitalResult]) -> float:
        """
        Calcula overall_score como média dos orbitais ativos
        
        Args:
            active_results: Lista de resultados de orbitais ativos
            
        Returns:
            Score geral (0-100)
        """
        if not active_results:
            return 0.0
        
        # Filtrar apenas resultados com score válido
        valid_results = [r for r in active_results if r.score is not None]
        
        if not valid_results:
            return 0.0
        
        # Média simples (pesos iguais por enquanto)
        total_score = sum(r.score for r in valid_results)
        avg_score = total_score / len(valid_results)
        
        return round(avg_score, 2)
    
    def _generate_insights(self, payload: Dict, active_results: List[OrbitalResult]) -> List[Dict]:
        """
        Gera insights heurísticos baseados nos resultados
        
        Args:
            payload: Payload da peça
            active_results: Resultados dos orbitais ativos
            
        Returns:
            Lista de insights
        """
        insights = []
        
        # Extrair informações do payload (suporta ambos formatos)
        text = self._extract_text_content(payload)
        
        # Tentar formato Creative Engine primeiro
        objective = payload.get("objective", {})
        if objective:
            goal = objective.get("primary_goal", "").lower()
        else:
            goal = payload.get("goal", "").lower()
        
        # Tentar formato Creative Engine primeiro
        distribution = payload.get("distribution", {})
        if distribution:
            context = distribution
        else:
            context = payload.get("context", {})
        
        format_type = context.get("format", "")
        
        # Buscar resultados por orbital_id
        results_by_id = {r.orbital_id: r for r in active_results}
        
        # Insight 1: CTA ausente e goal whatsapp_click
        semiotic_result = results_by_id.get("semiotic")
        if semiotic_result and semiotic_result.raw_features:
            cta_detected = semiotic_result.raw_features.get("cta_detected", False)
            if not cta_detected and goal == "whatsapp_click":
                insights.append({
                    "level": "high",
                    "title": "CTA ausente para objetivo WhatsApp",
                    "description": "O objetivo é gerar cliques no WhatsApp, mas nenhum CTA foi detectado no texto.",
                    "recommendation": "Adicione palavras-chave como 'chame', 'fale', 'whatsapp' ou 'zap' no texto."
                })
        
        # Insight 2: Overlay muito longo
        cognitive_result = results_by_id.get("cognitive")
        if cognitive_result and cognitive_result.raw_features:
            word_count = cognitive_result.raw_features.get("word_count", 0)
            ideal_limit = cognitive_result.raw_features.get("ideal_limit", 20)
            if word_count > ideal_limit * 1.5:
                insights.append({
                    "level": "medium",
                    "title": "Texto muito longo para o formato",
                    "description": f"O texto tem {word_count} palavras, mas o ideal para {format_type} é {ideal_limit}.",
                    "recommendation": "Reduza o texto para melhorar a legibilidade e engajamento."
                })
        
        # Insight 3: Urgência alta mas CTA fraco
        emotional_result = results_by_id.get("emotional")
        if emotional_result and semiotic_result:
            if emotional_result.raw_features and semiotic_result.raw_features:
                urgency_score = emotional_result.raw_features.get("urgency_score", 0.0)
                cta_keywords_found = semiotic_result.raw_features.get("cta_keywords_found", 0)
                if urgency_score > 0.5 and cta_keywords_found < 2:
                    insights.append({
                        "level": "medium",
                        "title": "Alta urgência sem CTA forte",
                        "description": "A peça transmite urgência, mas o CTA não está suficientemente destacado.",
                        "recommendation": "Reforce o call-to-action para capitalizar a urgência criada."
                    })
        
        # Insight 4: Coerência goal vs texto baixa
        if semiotic_result and semiotic_result.raw_features:
            goal_match = semiotic_result.raw_features.get("goal_match", 0.0)
            if goal_match < 0.4 and goal:
                insights.append({
                    "level": "medium",
                    "title": "Baixa coerência entre objetivo e texto",
                    "description": "O texto não reflete claramente o objetivo da peça.",
                    "recommendation": "Alinhe o conteúdo textual com o objetivo definido."
                })
        
        return insights
    
    def _extract_text_content(self, payload: Dict) -> str:
        """Extrai conteúdo textual do payload (suporta ambos formatos)"""
        # Tentar formato Creative Engine primeiro
        piece = payload.get("piece", {})
        if piece:
            text_overlay = piece.get("text_overlay", "")
            caption = piece.get("caption", "")
        else:
            # Fallback para formato antigo
            text_overlay = payload.get("text_overlay", "")
            caption = payload.get("caption", "")
        
        parts = [text_overlay, caption]
        return " ".join([p for p in parts if p])


def run_orbitals(payload: Dict) -> Dict:
    """
    Função helper para executar pipeline orbital
    
    Args:
        payload: Payload da peça do Creative Engine
        
    Returns:
        Dict com análise completa
    """
    pipeline = OrbitalPipeline()
    return pipeline.run_orbitals(payload)


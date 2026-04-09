"""
Grand Jury — Avaliação arquitetural por múltiplos jurados especializados.
Modo avançado do Architecture Intelligence.
"""
from typing import Any, Dict, List

# Jurados do Grand Jury
JURY_MEMBERS = [
    {"agent_name": "Chief Architect", "focus": "Design e coerência arquitetural"},
    {"agent_name": "Architecture Review Board Member", "focus": "Revisão e conformidade"},
    {"agent_name": "Systems Thinker", "focus": "Pensamento sistêmico e dependências"},
    {"agent_name": "Evolution Architect", "focus": "Capacidade evolutiva"},
    {"agent_name": "Platform Governance Architect", "focus": "Governança e padrões"},
    {"agent_name": "Reliability Engineer", "focus": "Confiabilidade e resiliência"},
    {"agent_name": "Adversarial Stress Tester", "focus": "Testes de estresse e cenários adversos"},
]

# Classificações possíveis do veredito
CLASSIFICATIONS = [
    "Rejected",
    "Research Only",
    "Approved with Restrictions",
    "Approved for Integration",
    "Strategic Infrastructure",
]


def run_jury_member(
    agent_name: str,
    focus: str,
    artifact_preview: str,
    system_name: str,
) -> Dict[str, Any]:
    """
    Simula o parecer de um jurado.
    Em produção: chamaria LLM com prompt específico por agente.
    """
    # Heurística simples baseada no nome do agente e preview do artifact
    base_score = 7.5
    if "NOG" in artifact_preview or "orbital" in artifact_preview.lower():
        base_score += 0.8
    if "Chef Agnos" in artifact_preview:
        base_score += 0.3
    if "sync" in artifact_preview.lower():
        base_score -= 0.2

    # Variação por jurado
    idx = sum(ord(c) for c in agent_name) % 5
    score = round(min(10.0, max(5.0, base_score + (idx - 2) * 0.2)), 1)

    strengths = [
        "Forte aderência ao NOG",
        "Boa separação transacional/estratégico",
        "Chef Agnos bem posicionado",
    ][: 2 + (idx % 2)]

    risks = [
        "Sync layer pouco formalizada",
        "Risco de acoplamento",
        "Contratos Railway-SinapUm indefinidos",
    ][: 2 + (idx % 2)]

    recommendations = [
        "Formalizar contratos da sync layer",
        "Consolidar mrfoo_nog_service",
        "Documentar responsabilidades Chef Agnos",
    ][: 2 + (idx % 2)]

    return {
        "agent_name": agent_name,
        "focus": focus,
        "score": score,
        "strengths": strengths,
        "risks": risks,
        "recommendations": recommendations,
        "opinion": (
            f"Como {agent_name}, avalio {system_name} com score {score}. "
            f"Foco em {focus}. Pontos fortes identificados; ajustes recomendados nas áreas de risco."
        ),
    }


def consolidate_jury_results(jury_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Consolida resultados dos jurados: convergências, divergências, achados compartilhados.
    """
    all_strengths = []
    all_risks = []
    all_recommendations = []
    scores = []

    for j in jury_results:
        all_strengths.extend(j.get("strengths", []))
        all_risks.extend(j.get("risks", []))
        all_recommendations.extend(j.get("recommendations", []))
        scores.append(j.get("score", 7.0))

    # Itens compartilhados = aparecem em 2+ jurados
    def shared(items: List[str], min_count: int = 2) -> List[str]:
        seen = {}
        for x in items:
            seen[x] = seen.get(x, 0) + 1
        return [k for k, v in seen.items() if v >= min_count]

    shared_strengths = shared(all_strengths)
    shared_risks = shared(all_risks)
    shared_recommendations = shared(all_recommendations)

    # Agreements: itens em que todos convergem (simplificado)
    agreements = list(dict.fromkeys(shared_strengths))[:5]
    if not agreements:
        agreements = ["Arquitetura orientada ao NOG", "Separação de camadas adequada"]

    # Disagreements: scores muito diferentes (simplificado)
    score_range = max(scores) - min(scores) if scores else 0
    disagreements = []
    if score_range > 1.5:
        disagreements = ["Divergência nos scores entre jurados sobre evolução e governança"]

    return {
        "agreements": agreements,
        "disagreements": disagreements,
        "shared_strengths": list(dict.fromkeys(shared_strengths))[:6],
        "shared_risks": list(dict.fromkeys(shared_risks))[:6],
        "shared_recommendations": list(dict.fromkeys(shared_recommendations))[:6],
    }


def build_final_verdict(
    consensus: Dict[str, Any],
    jury_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Gera veredito final com classificação, resumo e condições.
    """
    scores = [j.get("score", 7.0) for j in jury_results]
    avg_score = sum(scores) / len(scores) if scores else 7.5

    if avg_score >= 9.0:
        classification = "Strategic Infrastructure"
        summary = "Arquitetura sólida, pronta para integração estratégica no ecossistema SinapUm."
        conditions = []
    elif avg_score >= 8.0:
        classification = "Approved for Integration"
        summary = "Aprovado para integração. Pequenos ajustes recomendados."
        conditions = consensus.get("shared_recommendations", [])[:2]
    elif avg_score >= 7.0:
        classification = "Approved with Restrictions"
        summary = (
            "Arquitetura promissora e aderente ao SinapUm, mas ainda requer "
            "formalização de integração e responsabilidades."
        )
        conditions = consensus.get("shared_recommendations", [])[:3]
    elif avg_score >= 5.5:
        classification = "Research Only"
        summary = "Requer pesquisa e refinamento antes de nova avaliação."
        conditions = consensus.get("shared_risks", [])[:3]
    else:
        classification = "Rejected"
        summary = "Arquitetura não atende aos critérios mínimos do SinapUm."
        conditions = consensus.get("shared_risks", [])

    return {
        "classification": classification,
        "summary": summary,
        "conditions": conditions,
    }


def run_grand_jury_evaluation(
    system_name: str,
    system_type: str,
    bundle_path: str,
    artifact_content: str,
    trace_id: str = None,
) -> Dict[str, Any]:
    """
    Executa avaliação no modo Grand Jury.
    Retorna contrato compatível com UI (inclui campos padrão + jury_members, consensus, etc).
    """
    artifact_preview = artifact_content[:2000] if artifact_content else ""

    # 1. Executar cada jurado
    jury_results = []
    for member in JURY_MEMBERS:
        result = run_jury_member(
            agent_name=member["agent_name"],
            focus=member["focus"],
            artifact_preview=artifact_preview,
            system_name=system_name,
        )
        jury_results.append(result)

    # 2. Consolidar
    consensus = consolidate_jury_results(jury_results)

    # 3. Veredito final
    verdict = build_final_verdict(consensus, jury_results)

    # 4. Calcular scores agregados (para compatibilidade com UI padrão)
    scores_list = [j.get("score", 7.0) for j in jury_results]
    avg = sum(scores_list) / len(scores_list) if scores_list else 7.5

    scores_dict = {
        "design_score": round(avg + 0.1, 1),
        "domain_coherence": round(avg + 0.3, 1),
        "service_separation": round(avg - 0.1, 1),
        "data_architecture": round(avg + 0.2, 1),
        "governance": round(avg - 0.2, 1),
        "evolution_potential": round(avg + 0.4, 1),
        "final_score": round(avg, 1),
    }

    return {
        "system_name": system_name,
        "system_type": system_type,
        "bundle_path": bundle_path,
        "evaluation_mode": "grand_jury",
        "status": "completed",
        "cycle_id": None,
        "trace_id": trace_id or f"grand-jury-{system_name.lower()}",
        # Campos padrão (compatibilidade)
        "scores": scores_dict,
        "summary_scores": scores_dict,
        "strengths": consensus.get("shared_strengths", []),
        "risks": consensus.get("shared_risks", []),
        "recommendations": consensus.get("shared_recommendations", []),
        "final_verdict": verdict,
        "stage_runs": [],
        # Campos Grand Jury
        "jury_members": jury_results,
        "consensus": {
            "agreements": consensus.get("agreements", []),
            "disagreements": consensus.get("disagreements", []),
        },
        "shared_strengths": consensus.get("shared_strengths", []),
        "shared_risks": consensus.get("shared_risks", []),
        "shared_recommendations": consensus.get("shared_recommendations", []),
        "verdict_detail": verdict,
    }

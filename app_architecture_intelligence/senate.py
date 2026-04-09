"""
Architecture Senate — Deliberação institucional sobre avaliação arquitetural.
Modo avançado que executa o Grand Jury e adiciona debate, consenso e veredito institucional.

Ponto de extensão futura: conectar múltiplos prompts/LLM para debate real entre agentes.
"""
from typing import Any, Dict, List

# Tópicos padrão para debate (derivados do domínio SinapUm)
DEFAULT_DEBATE_TOPICS = [
    "domínio arquitetural",
    "separação de serviços",
    "sync layer",
    "arquitetura de dados",
    "governança",
    "evolução",
    "confiabilidade",
]

# Níveis de acordo
AGREEMENT_LEVELS = ["high", "medium", "low"]

# Classificações do veredito (institucional)
SENATE_CLASSIFICATIONS = [
    "Rejected",
    "Research Only",
    "Approved with Restrictions",
    "Approved for Integration",
    "Strategic Infrastructure",
]


def extract_debate_topics(jury_report: Dict[str, Any]) -> List[str]:
    """
    Extrai tópicos principais a partir de risks, recommendations e opiniões dos jurados.
    Ponto de extensão: LLM poderia inferir tópicos mais refinados.
    """
    topics = set()
    jury_members = jury_report.get("jury_members", [])
    for j in jury_members:
        for r in j.get("risks", []):
            if "sync" in r.lower():
                topics.add("sync layer")
            elif "acoplamento" in r.lower() or "contrato" in r.lower():
                topics.add("separação de serviços")
            elif "governança" in r.lower():
                topics.add("governança")
            elif "nog" in r.lower() or "domínio" in r.lower():
                topics.add("domínio arquitetural")
            elif "dados" in r.lower():
                topics.add("arquitetura de dados")
        for rec in j.get("recommendations", []):
            if "formalizar" in rec.lower():
                topics.add("sync layer")
            if "evolução" in rec.lower():
                topics.add("evolução")
            if "confiabilidade" in rec.lower():
                topics.add("confiabilidade")
    result = list(topics) if topics else DEFAULT_DEBATE_TOPICS[:5]
    return result[:7]


def run_senate_debate(jury_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Gera debate entre jurados sobre tópicos identificados.
    Cada tópico tem entries com posições e respostas cruzadas.
    Mock estruturado — preparado para LLM calls por agente.
    """
    topics = extract_debate_topics(jury_report)
    jury_members = jury_report.get("jury_members", [])
    agent_names = [j.get("agent_name", "") for j in jury_members if j.get("agent_name")]

    debate_result = []
    for topic in topics:
        entries = []
        # Posição inicial de 2-3 agentes
        for i, agent in enumerate(agent_names[:4]):
            if topic == "sync layer":
                positions = [
                    "A solução atual é aceitável para MVP.",
                    "Existe risco de SPOF na sync layer sem formalização de fallback.",
                    "A sync layer precisa de contratos explícitos entre Railway e SinapUm.",
                    "Recomendo formalizar antes do rollout.",
                ]
            elif topic == "governança":
                positions = [
                    "O nível de maturidade da governança é adequado para orbital.",
                    "A governança ainda requer documentação de responsabilidades.",
                    "Há dispersão de regras do NOG em múltiplas camadas.",
                ]
            elif topic == "domínio arquitetural":
                positions = [
                    "Forte aderência ao NOG e coerência de domínio.",
                    "O domínio está bem modelado, Chef Agnos bem posicionado.",
                    "Boa separação entre transacional e estratégico.",
                ]
            else:
                positions = [
                    f"O tópico {topic} merece atenção.",
                    f"Convergência parcial sobre {topic}.",
                ]
            pos = positions[i % len(positions)]
            entries.append({"agent_name": agent, "position": pos})

        # Resposta cruzada (simula debate)
        if len(entries) >= 2:
            idx = sum(ord(c) for c in topic) % len(entries)
            responder = agent_names[(idx + 2) % len(agent_names)] if agent_names else ""
            if responder and responder != entries[0].get("agent_name"):
                entries.append({
                    "agent_name": responder,
                    "position": "Discordo parcialmente. A formalização deve ser prioridade.",
                    "responds_to": entries[0].get("agent_name"),
                })

        # Resultado do debate por tópico
        if "sync" in topic.lower():
            debate_result_str = "Risco confirmado com necessidade de formalização."
        elif "governança" in topic.lower():
            debate_result_str = "Divergência sobre maturidade; documentação recomendada."
        else:
            debate_result_str = "Convergência parcial; ajustes recomendados."

        debate_result.append({
            "topic": topic,
            "entries": entries,
            "debate_result": debate_result_str,
        })

    return debate_result


def build_consensus_matrix(
    jury_report: Dict[str, Any],
    senate_debate: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Constrói matriz de consenso por tópico.
    agreement_level: high | medium | low
    """
    matrix = []
    for d in senate_debate:
        topic = d.get("topic", "")
        entries_count = len(d.get("entries", []))
        # Heurística: mais entries com posições similares = maior acordo
        if "sync" in topic.lower():
            level = "medium"
            notes = "Há consenso sobre risco, mas divergência sobre gravidade."
        elif "domínio" in topic.lower() or "nog" in topic.lower():
            level = "high"
            notes = "Os agentes convergem sobre a força do domínio."
        elif "governança" in topic.lower():
            level = "low"
            notes = "Os agentes divergem sobre o nível de maturidade da governança."
        elif "separação" in topic.lower():
            level = "high"
            notes = "Alta convergência sobre separação de camadas."
        else:
            level = "medium" if entries_count >= 3 else "low"
            notes = f"Convergência parcial sobre {topic}."

        matrix.append({
            "topic": topic,
            "agreement_level": level,
            "notes": notes,
        })
    return matrix


def build_senate_verdict(
    jury_report: Dict[str, Any],
    consensus_matrix: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Gera veredito institucional do Senado.
    Mais formal que o veredito do Grand Jury.
    """
    jury_members = jury_report.get("jury_members", [])
    scores = [j.get("score", 7.0) for j in jury_members]
    avg_score = sum(scores) / len(scores) if scores else 7.5

    shared_recs = jury_report.get("shared_recommendations", [])
    shared_risks = jury_report.get("shared_risks", [])

    high_agreement = sum(1 for m in consensus_matrix if m.get("agreement_level") == "high")
    total_topics = len(consensus_matrix) or 1
    agreement_ratio = high_agreement / total_topics

    if avg_score >= 9.0 and agreement_ratio >= 0.6:
        classification = "Strategic Infrastructure"
        summary = "A arquitetura é sólida e pronta para integração estratégica no ecossistema SinapUm."
        conditions = []
        strategic_potential = "high"
    elif avg_score >= 8.0:
        classification = "Approved for Integration"
        summary = "Aprovado para integração. Pequenos ajustes recomendados."
        conditions = shared_recs[:2]
        strategic_potential = "high"
    elif avg_score >= 7.0:
        classification = "Approved with Restrictions"
        summary = (
            "A arquitetura do orbital é promissora e aderente ao SinapUm, "
            "mas requer formalização de integração e governança."
        )
        conditions = shared_recs[:3]
        strategic_potential = "medium"
    elif avg_score >= 5.5:
        classification = "Research Only"
        summary = "Requer pesquisa e refinamento antes de nova avaliação."
        conditions = shared_risks[:3]
        strategic_potential = "low"
    else:
        classification = "Rejected"
        summary = "Arquitetura não atende aos critérios mínimos do SinapUm."
        conditions = shared_risks
        strategic_potential = "low"

    return {
        "classification": classification,
        "summary": summary,
        "conditions": conditions,
        "strategic_potential": strategic_potential,
    }


def run_senate_evaluation(
    system_name: str,
    system_type: str,
    bundle_path: str,
    artifact_content: str,
    trace_id: str = None,
) -> Dict[str, Any]:
    """
    Executa avaliação no modo Architecture Senate.
    1. Chama Grand Jury (reutiliza 100%)
    2. Gera debate entre jurados
    3. Constrói matriz de consenso
    4. Emite veredito institucional

    Retorna contrato compatível com UI (inclui jury_members + senate_debate + consensus_matrix + senate_verdict).
    """
    from .grand_jury import run_grand_jury_evaluation

    jury_report = run_grand_jury_evaluation(
        system_name=system_name,
        system_type=system_type,
        bundle_path=bundle_path,
        artifact_content=artifact_content,
        trace_id=trace_id or f"senate-{system_name.lower()}",
    )

    senate_debate = run_senate_debate(jury_report)
    consensus_matrix = build_consensus_matrix(jury_report, senate_debate)
    senate_verdict = build_senate_verdict(jury_report, consensus_matrix)

    return {
        "system_name": system_name,
        "system_type": system_type,
        "bundle_path": bundle_path,
        "evaluation_mode": "senate",
        "status": "completed",
        "cycle_id": jury_report.get("cycle_id"),
        "trace_id": trace_id or f"senate-{system_name.lower()}",
        "scores": jury_report.get("scores", {}),
        "summary_scores": jury_report.get("summary_scores", jury_report.get("scores", {})),
        "strengths": jury_report.get("strengths", []),
        "risks": jury_report.get("risks", []),
        "recommendations": jury_report.get("recommendations", []),
        "final_verdict": senate_verdict,
        "stage_runs": [],
        "jury_members": jury_report.get("jury_members", []),
        "consensus": jury_report.get("consensus", {}),
        "shared_strengths": jury_report.get("shared_strengths", []),
        "shared_risks": jury_report.get("shared_risks", []),
        "shared_recommendations": jury_report.get("shared_recommendations", []),
        "verdict_detail": senate_verdict,
        "senate_debate": senate_debate,
        "consensus_matrix": consensus_matrix,
        "senate_verdict": senate_verdict,
    }

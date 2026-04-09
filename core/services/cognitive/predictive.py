"""
Predictive leve (heurísticas) — sem ML pesado.
Produz lista de riscos e score agregado para incluir no prompt do LLM.
"""
from typing import Any, Dict, List


def prever_riscos(contexto: Dict[str, Any]) -> Dict[str, Any]:
    """
    contexto pode conter: user_text, route, tags, channel, etc.
    """
    text = (contexto.get("user_text") or contexto.get("text") or "").strip().lower()
    route = (contexto.get("route") or "").strip().lower()
    riscos: List[Dict[str, Any]] = []

    if len(text) < 2:
        riscos.append({"tipo": "input_muito_curto", "severidade": "baixa"})
    if any(w in text for w in ("cancelar", "estorno", "reclamação", "reclamacao", "procon", "advogado")):
        riscos.append({"tipo": "atencao_cliente", "severidade": "media"})
    if any(w in text for w in ("urgente", "agora", "imediato")):
        riscos.append({"tipo": "urgencia_declarada", "severidade": "baixa"})
    if route in ("support", "handoff", "humano"):
        riscos.append({"tipo": "rota_manual_ou_escalacao", "severidade": "baixa"})

    score = min(1.0, len(riscos) * 0.22)
    return {"riscos": riscos, "score": round(score, 3)}

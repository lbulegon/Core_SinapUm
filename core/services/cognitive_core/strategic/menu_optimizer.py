"""
Sugestões de cardápio a partir de KPIBundle (dados já agregados — sem ORM MrFoo no Core).
"""
from __future__ import annotations

from typing import Any, Dict, List

from core.services.cognitive_core.strategic.strategy_models import KPIBundle


def menu_suggestions_from_kpi(kpi: KPIBundle) -> List[Dict[str, Any]]:
    """
    Por produto: score ~ receita / minuto de preparo; acão heurística (alinhada a AcoesOperacionais / estratégia).
    """
    out: List[Dict[str, Any]] = []
    for p in kpi.por_produto:
        t = max(0.01, float(p.tempo_prep_medio_min))
        receita = float(p.receita)
        score = receita / max(t, 1.0)
        if t > 15:
            acao = "reduzir_complexidade"
        elif score < 10:
            acao = "remover_item"
        else:
            acao = "priorizar_item"
        out.append(
            {
                "item_id": p.item_id,
                "nome": p.nome,
                "acao": acao,
                "score": round(score, 4),
                "tempo_prep_medio_min": round(t, 2),
                "margem_pct": p.margem_pct,
                "lucro_por_hora_prep": p.lucro_por_hora_prep,
            }
        )
    out.sort(key=lambda x: float(x.get("score") or 0), reverse=True)
    return out[:30]


def analyze_menu_aggregates(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Entrada genérica (ex.: agregação feita no MrFoo): produto_id/item_id, quantidade, tempo_medio, receita_total.
    """
    out: List[Dict[str, Any]] = []
    for r in rows or []:
        pid = str(r.get("produto_id") or r.get("item_id") or "")
        if not pid:
            continue
        q = float(r.get("quantidade") or r.get("total_vendas") or 1)
        t = float(r.get("tempo_medio") or r.get("tempo_prep_medio_min") or 15)
        rec = float(r.get("receita_total") or r.get("receita") or 0)
        score = rec / max(t, 1.0)
        if t > 15:
            acao = "reduzir_complexidade"
        elif score < 10:
            acao = "remover_item"
        else:
            acao = "priorizar_item"
        out.append(
            {
                "produto_id": pid,
                "acao": acao,
                "score": round(score, 4),
            }
        )
    out.sort(key=lambda x: x["score"], reverse=True)
    return out

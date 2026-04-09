"""
Otimização de portefólio multi-loja: compara lojas a partir de métricas agregadas (sem ORM obrigatório).
Entrada típica: lista de dicts vindos do painel / MrFoo por tenant_id.
"""
from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional


def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def analyze_multi_store_portfolio(stores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Agrega sinais e sugere realocação de foco / playbooks entre lojas.

    Cada loja pode trazer: tenant_id, receita, margem_media_pct, carga_estimada (0–1),
    atraso_medio_segundos, pedidos_ativos_count, nome (opcional).
    """
    rows = [s for s in (stores or []) if isinstance(s, dict) and str(s.get("tenant_id") or "").strip()]
    if not rows:
        return {
            "ok": True,
            "stores_count": 0,
            "benchmark": {},
            "ranking": [],
            "recommendations": [],
        }

    margens = [_f(r.get("margem_media_pct")) for r in rows]
    cargas = [_f(r.get("carga_estimada")) for r in rows]
    atrasos = [_f(r.get("atraso_medio_segundos")) for r in rows]
    receitas = [_f(r.get("receita")) for r in rows]

    med_m = statistics.median(margens) if margens else 0.0
    med_a = statistics.median(atrasos) if atrasos else 0.0
    tot_rec = sum(receitas) or 1.0

    scored: List[Dict[str, Any]] = []
    for r in rows:
        tid = str(r.get("tenant_id"))
        m = _f(r.get("margem_media_pct"))
        c = _f(r.get("carga_estimada"))
        a = _f(r.get("atraso_medio_segundos"))
        rec = _f(r.get("receita"))
        share = rec / tot_rec
        # score portefólio: margem acima da mediana e atraso abaixo da mediana = melhor
        margin_score = (m - med_m) / max(med_m, 1.0) if med_m > 0 else 0.0
        delay_penalty = (a - med_a) / max(med_a, 1.0) if med_a > 0 else 0.0
        load_stress = max(0.0, c - 0.75) * 2.0
        health = margin_score - 0.4 * delay_penalty - load_stress + 0.15 * min(1.0, share * 3)
        scored.append(
            {
                "tenant_id": tid,
                "nome": r.get("nome") or tid,
                "receita_share": round(share, 4),
                "margem_media_pct": m,
                "carga_estimada": c,
                "atraso_medio_segundos": a,
                "health_score": round(max(-1.0, min(1.5, health)), 4),
            }
        )

    scored.sort(key=lambda x: x["health_score"], reverse=True)
    worst = scored[-1] if scored else None
    best = scored[0] if scored else None

    recs: List[Dict[str, Any]] = []
    if worst and best and worst["tenant_id"] != best["tenant_id"]:
        recs.append(
            {
                "tipo": "transferir_playbook_operacional",
                "de_tenant": best["tenant_id"],
                "para_tenant": worst["tenant_id"],
                "motivo": "Diferencial de health_score entre topo e cauda do portefólio.",
            }
        )
    for s in scored:
        if s["carga_estimada"] > 0.88 and s["atraso_medio_segundos"] > med_a * 1.25:
            recs.append(
                {
                    "tipo": "capacidade_antes_de_crescimento",
                    "tenant_id": s["tenant_id"],
                    "motivo": "Carga e atraso acima do par — priorizar throughput antes de novas campanhas.",
                }
            )
        if s["margem_media_pct"] < med_m * 0.85 and s["receita_share"] > 0.2:
            recs.append(
                {
                    "tipo": "revisao_precificacao_cardapio",
                    "tenant_id": s["tenant_id"],
                    "motivo": "Peso de receita alto com margem abaixo do benchmark do grupo.",
                }
            )

    return {
        "ok": True,
        "stores_count": len(rows),
        "benchmark": {
            "margem_mediana_pct": round(med_m, 2),
            "atraso_mediano_segundos": round(med_a, 2),
            "receita_total": round(tot_rec, 2),
        },
        "ranking": scored,
        "recommendations": recs[:15],
    }

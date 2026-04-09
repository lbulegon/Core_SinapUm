"""
Liga o simulador de estações ao Chef Agno (dry-run): score, categoria, prioridade.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from core.cognition.chef_agno.simulator import dry_run


def aplicar_prioridade_chef_agno(
    pedido_sim: Dict[str, Any],
    *,
    estado_operacional: Optional[Dict[str, Any]] = None,
    tempo_espera: float = 0.0,
    peso_tempo: float = 0.5,
    origem: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Preenche `prioridade`, `chef_agno_score`, `chef_agno_categoria`, `chef_agno_acao`, `previsao_gargalo`.
    `pedido_sim` deve ter chave `pedido` (itens/valor) ou ser o próprio dict de cardápio.
    """
    pedido_card = pedido_sim.get("pedido")
    if pedido_card is None:
        pedido_card = {
            "itens": pedido_sim.get("itens", []),
            "valor_total": pedido_sim.get("valor_total", 0.0),
        }

    ev: Dict[str, Any] = {
        "evento": "pedido_recebido",
        "event_id": str(pedido_sim.get("id", pedido_sim.get("pedido_id", "sim"))),
        "origem": origem
        or pedido_sim.get("origem")
        or {"canal": "IFOOD", "externo_id": str(pedido_sim.get("id", ""))},
        "pedido": pedido_card,
    }
    if estado_operacional:
        ev["operational_snapshot"] = estado_operacional
    if pedido_sim.get("timestamp"):
        ev["timestamp"] = pedido_sim["timestamp"]
    if pedido_sim.get("empresa_id") is not None:
        ev["empresa_id"] = pedido_sim["empresa_id"]
    if pedido_sim.get("contexto"):
        ev["contexto"] = pedido_sim["contexto"]

    dr = dry_run(ev)
    score = float(dr["score"])
    pedido_sim["chef_agno_score"] = score
    pedido_sim["chef_agno_categoria"] = dr["categoria"]
    pedido_sim["chef_agno_acao"] = dr["acao_recomendada"]
    pedido_sim["previsao_gargalo"] = dr["previsao_gargalo"]
    pedido_sim["prioridade"] = score + float(tempo_espera) * float(peso_tempo)
    return dr

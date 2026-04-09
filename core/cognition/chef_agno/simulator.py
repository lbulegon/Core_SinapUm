"""
Simulador de cozinha — dry-run das decisões do Chef Agno, previsão de gargalo e dataset sintético.

Não chama MrFoo nem APIs externas. Útil para calibrar limiares, gerar JSONL de treino e ensaiar políticas.
"""

from __future__ import annotations

import copy
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

from django.conf import settings

from core.cognition.chef_agno.features import carga_operacional_de_snapshot
from core.cognition.chef_agno.scorer import avaliar


def estado_inicial_padrao() -> Dict[str, Any]:
    """Métricas alinhadas ao snapshot operacional (MrFoo / RealityState)."""
    return {
        "pedidos_ativos_count": 0,
        "fila_em_preparo": 0,
        "fila_confirmado": 0,
        "atraso_medio_segundos": 0,
        "tempo_medio_preparo_segundos": 900,
    }


def snapshot_de_estado(estado: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "pedidos_ativos_count": int(estado.get("pedidos_ativos_count", 0)),
        "fila_em_preparo": int(estado.get("fila_em_preparo", 0)),
        "fila_confirmado": int(estado.get("fila_confirmado", 0)),
        "atraso_medio_segundos": int(estado.get("atraso_medio_segundos", 0)),
        "tempo_medio_preparo_segundos": int(estado.get("tempo_medio_preparo_segundos", 900)),
    }


def prever_gargalo(
    estado: Dict[str, Any],
    *,
    incremento_carga: float = 0.12,
) -> Dict[str, Any]:
    """
    Projeção pessimista curta: carga atual + incremento (ex.: mais 3–5 pedidos na janela).
    """
    snap = snapshot_de_estado(estado)
    c0 = carga_operacional_de_snapshot(snap)
    c1 = min(1.0, c0 + float(incremento_carga))
    lim = float(getattr(settings, "CHEF_AGNO_GARGALO_LIMITE", 0.85))
    risco = c1 >= lim
    return {
        "carga_atual": round(c0, 4),
        "carga_prevista_curto_prazo": round(c1, 4),
        "limiar_gargalo": lim,
        "risco_gargalo": risco,
        "recomendacao": (
            "mitigar_entrada_pedidos_complexos" if risco else "operacao_dentro_do_normal"
        ),
    }


def montar_evento(
    *,
    pedido: Dict[str, Any],
    estado: Dict[str, Any],
    origem: Optional[Dict[str, str]] = None,
    contexto_extra: Optional[Dict[str, Any]] = None,
    event_id: Optional[str] = None,
    hora_simulada: Optional[int] = None,
    empresa_id: Optional[int] = None,
) -> Dict[str, Any]:
    origem = origem or {"canal": "IFOOD", "externo_id": f"sim-{uuid.uuid4().hex[:8]}"}
    ctx: Dict[str, Any] = {
        "tempo_medio_preparo_segundos": int(estado.get("tempo_medio_preparo_segundos", 900)),
    }
    if contexto_extra:
        ctx.update(contexto_extra)
    pred = prever_gargalo(estado)
    ctx["carga_prevista"] = pred["carga_prevista_curto_prazo"]

    ev: Dict[str, Any] = {
        "evento": "pedido_recebido",
        "event_id": event_id or f"sim-{uuid.uuid4().hex}",
        "origem": dict(origem),
        "pedido": copy.deepcopy(pedido),
        "operational_snapshot": snapshot_de_estado(estado),
        "contexto": ctx,
    }
    if hora_simulada is not None:
        ev["timestamp"] = f"2025-06-01T{int(hora_simulada):02d}:30:00+00:00"
    if empresa_id is not None:
        ev["empresa_id"] = int(empresa_id)
    return ev


def dry_run(evento: Dict[str, Any]) -> Dict[str, Any]:
    """Avalia política + modelo sem efeitos colaterais."""
    acao, score, features = avaliar(evento)
    from core.cognition.chef_agno.policy import categoria_por_score

    snap = evento.get("operational_snapshot") or {}
    estado_implicito = {
        "pedidos_ativos_count": snap.get("pedidos_ativos_count", 0),
        "fila_em_preparo": snap.get("fila_em_preparo", 0),
        "fila_confirmado": snap.get("fila_confirmado", 0),
        "atraso_medio_segundos": snap.get("atraso_medio_segundos", 0),
    }
    gargalo = prever_gargalo(estado_implicito)
    return {
        "acao_recomendada": acao,
        "score": score,
        "categoria": categoria_por_score(score),
        "features": features,
        "previsao_gargalo": gargalo,
    }


def aplicar_acao_no_estado(
    estado: Dict[str, Any],
    acao: str,
    *,
    pedido_entrou_confirmado: bool = True,
) -> Dict[str, Any]:
    """
    Transição *toy* para encadear ticks (não substitui simulação real de filas).
    """
    s = copy.deepcopy(estado)
    if acao == "confirmar_pedido" and pedido_entrou_confirmado:
        s["pedidos_ativos_count"] = int(s.get("pedidos_ativos_count", 0)) + 1
        s["fila_confirmado"] = int(s.get("fila_confirmado", 0)) + 1
    elif acao == "postergar_pedido":
        s["fila_confirmado"] = int(s.get("fila_confirmado", 0)) + 1
    elif acao == "reordenar_fila":
        fc = int(s.get("fila_confirmado", 0))
        fp = int(s.get("fila_em_preparo", 0))
        if fc > 0:
            s["fila_confirmado"] = fc - 1
            s["fila_em_preparo"] = fp + 1
    return s


def simular_sequencia(
    passos: List[Dict[str, Any]],
    estado_inicial: Optional[Dict[str, Any]] = None,
    *,
    hora_fixa: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Cada passo: { "pedido": {...}, "origem"?: {}, "contexto"?: {}, "empresa_id"?: int }
    """
    estado = copy.deepcopy(estado_inicial or estado_inicial_padrao())
    saida: List[Dict[str, Any]] = []
    for i, passo in enumerate(passos):
        pedido = passo.get("pedido") or {}
        ev = montar_evento(
            pedido=pedido,
            estado=estado,
            origem=passo.get("origem"),
            contexto_extra=passo.get("contexto"),
            event_id=passo.get("event_id") or f"seq-{i}",
            hora_simulada=hora_fixa if hora_fixa is not None else passo.get("hora_dia"),
            empresa_id=passo.get("empresa_id"),
        )
        dr = dry_run(ev)
        acao = dr["acao_recomendada"]
        estado = aplicar_acao_no_estado(estado, acao)
        saida.append(
            {
                "passo": i,
                "evento": ev,
                "dry_run": dr,
                "estado_apos": snapshot_de_estado(estado),
            }
        )
    return saida


# --- Cenários prontos (presets) -------------------------------------------------

def _pedido_simples() -> Dict[str, Any]:
    return {"itens": [{"nome": "X", "modificadores": []}], "valor_total": 35.0}


def _pedido_pesado() -> Dict[str, Any]:
    mods = [f"m{i}" for i in range(6)]
    return {
        "itens": [
            {"nome": "A", "modificadores": mods[:3]},
            {"nome": "B", "modificadores": mods[3:]},
        ],
        "valor_total": 180.0,
    }


CENARIOS_PRESET: Dict[str, Dict[str, Any]] = {
    "calma": {
        "estado": {
            "pedidos_ativos_count": 3,
            "fila_em_preparo": 1,
            "fila_confirmado": 2,
            "atraso_medio_segundos": 120,
        },
        "pedido": _pedido_simples(),
    },
    "pico": {
        "estado": {
            "pedidos_ativos_count": 28,
            "fila_em_preparo": 10,
            "fila_confirmado": 12,
            "atraso_medio_segundos": 840,
        },
        "pedido": _pedido_simples(),
        "hora_dia": 20,
    },
    "complexo_em_pico": {
        "estado": {
            "pedidos_ativos_count": 22,
            "fila_em_preparo": 8,
            "fila_confirmado": 9,
            "atraso_medio_segundos": 600,
        },
        "pedido": _pedido_pesado(),
        "hora_dia": 20,
    },
    "noite_tardia": {
        "estado": {
            "pedidos_ativos_count": 6,
            "fila_em_preparo": 2,
            "fila_confirmado": 3,
            "atraso_medio_segundos": 400,
        },
        "pedido": _pedido_pesado(),
        "hora_dia": 23,
    },
}


def executar_preset(nome: str) -> Dict[str, Any]:
    if nome not in CENARIOS_PRESET:
        raise KeyError(f"Cenário desconhecido: {nome}. Opções: {sorted(CENARIOS_PRESET)}")
    spec = CENARIOS_PRESET[nome]
    estado = {**estado_inicial_padrao(), **spec["estado"]}
    ev = montar_evento(
        pedido=spec["pedido"],
        estado=estado,
        hora_simulada=spec.get("hora_dia"),
        event_id=f"preset-{nome}",
    )
    dr = dry_run(ev)
    return {
        "preset": nome,
        "evento": ev,
        "dry_run": dr,
        "estado_inicial_snapshot": snapshot_de_estado(estado),
    }


def executar_todos_presets() -> List[Dict[str, Any]]:
    return [executar_preset(n) for n in sorted(CENARIOS_PRESET.keys())]


def exportar_para_dataset(
    resultados: List[Dict[str, Any]],
    *,
    fonte: str = "simulador_cozinha",
    registrar: Optional[Callable[..., None]] = None,
) -> int:
    """
    Grava linhas via `registrar_resultado` (ou função injetada) para JSONL de treino.
    Retorna quantidade de linhas escritas.
    """
    reg = registrar
    if reg is None:
        from core.cognition.chef_agno.trainer import registrar_resultado as reg

    n = 0
    for bloco in resultados:
        if "evento" not in bloco or "dry_run" not in bloco:
            continue
        ev = bloco["evento"]
        dr = bloco["dry_run"]
        if "preset" in bloco:
            cenario = bloco["preset"]
        elif "passo" in bloco:
            cenario = f"sequencia_passo_{bloco['passo']}"
        else:
            cenario = bloco.get("cenario_id", "simulacao")
        reg(
            ev,
            dr["acao_recomendada"],
            {
                "categoria": dr["categoria"],
                "previsao_gargalo": dr["previsao_gargalo"],
                "simulado": True,
            },
            features=dr["features"],
            score=dr["score"],
            meta={"fonte": fonte, "cenario_id": str(cenario)},
        )
        n += 1
    return n

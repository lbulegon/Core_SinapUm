from __future__ import annotations

from collections import Counter
from typing import Any


def _iter_pedidos(pedidos_queryset: Any):
    if pedidos_queryset is None:
        return []
    if hasattr(pedidos_queryset, "all"):
        return pedidos_queryset.all()
    if isinstance(pedidos_queryset, (list, tuple)):
        return pedidos_queryset
    return list(pedidos_queryset)


def _infer_status(pedido: Any) -> str | None:
    for field in ("status", "estado", "state", "situacao"):
        raw = getattr(pedido, field, None)
        if raw is None:
            continue
        if hasattr(raw, "name"):  # enum-like
            return str(getattr(raw, "name", raw)).lower()
        return str(raw).lower()
    return None


def _is_preparo_status(status: str | None) -> bool:
    if not status:
        return False
    tokens = (
        "preparo",
        "prepara",
        "cozinha",
        "producao",
        "kds",
        "em_andamento",
        "andamento",
        "cooking",
        "in_progress",
        "preparing",
    )
    return any(t in status for t in tokens)


def _tempo_real_minutos(pedido: Any) -> float | None:
    for field in (
        "tempo_preparo_real",
        "tempo_real_preparo",
        "lead_time_minutos",
        "tempo_execucao_minutos",
        "tempo_total_minutos",
    ):
        val = getattr(pedido, field, None)
        if val is None:
            continue
        try:
            return float(val)
        except Exception:
            continue
    return None


def enrich_operational_context(
    base: dict[str, Any] | None,
    pedidos_queryset: Any | None,
) -> dict[str, Any]:
    """
    Enriquece contexto operacional com sinais derivados do queryset (best effort).
    Nunca falha: retorna sempre um dict.
    """
    ctx = dict(base or {})
    pedidos = list(_iter_pedidos(pedidos_queryset))

    preparo = 0
    tempos: list[float] = []
    estacoes = Counter()

    for pedido in pedidos:
        st = _infer_status(pedido)
        if _is_preparo_status(st):
            preparo += 1

        tr = _tempo_real_minutos(pedido)
        if tr is not None and tr > 0:
            tempos.append(tr)

        # Ocupação por estação (se existir no modelo)
        estacao = getattr(pedido, "estacao", None) or getattr(pedido, "station", None)
        if estacao is not None:
            label = getattr(estacao, "nome", None) or getattr(estacao, "name", None) or str(estacao)
            estacoes[str(label)] += 1

    ctx.setdefault("pedidos_em_preparo", preparo)
    if tempos:
        ctx.setdefault("tempo_medio_real_min", sum(tempos) / len(tempos))
    if estacoes:
        ctx.setdefault("ocupacao_por_estacao", dict(estacoes))

    # Compat: se vier só carga manual, mantém; senão, deriva um proxy simples
    if "carga_cozinha" not in ctx or ctx.get("carga_cozinha") in (None, "", 0, 0.0):
        # Heurística leve: preparo + fila recente (sem assumir schema)
        ctx["carga_cozinha"] = float(preparo)

    return ctx

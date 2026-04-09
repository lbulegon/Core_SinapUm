import re
from typing import Any, Dict, List


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(".", "").replace(",", ".")
    try:
        return float(text)
    except (TypeError, ValueError):
        return default


def _normalize_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        produto = str(item.get("produto") or "").strip().lower()
        if not produto:
            continue
        quantidade = _to_float(item.get("quantidade"), default=1.0)
        valor = _to_float(item.get("valor"), default=0.0)
        unidade = str(item.get("unidade") or "un").strip().lower()
        out.append({
            "produto": produto[:255],
            "quantidade": quantidade if quantidade > 0 else 1.0,
            "unidade": unidade[:20] or "un",
            "valor": max(0.0, valor),
        })
    return out


def _parse_items(texto: str) -> List[Dict[str, Any]]:
    texto = (texto or "").lower().strip()
    if not texto:
        return []

    parts = re.split(r",|\s+e\s+", texto)
    items: List[Dict[str, Any]] = []
    pattern_qty_por = re.compile(
        r"(?P<qtd>\d+(?:[.,]\d+)?)\s*(?P<un>[a-zA-Z]{1,10})?\s+de\s+(?P<prod>.+?)\s+por\s+(?P<valor>\d+(?:[.,]\d+)?)$"
    )
    pattern_prod_val = re.compile(
        r"(?P<prod>[a-zA-ZÀ-ÿ0-9\s\-_/]+?)\s+(?P<valor>\d+(?:[.,]\d+)?)$"
    )

    for raw in parts:
        part = raw.strip(" .;")
        if not part:
            continue
        part = re.sub(r"^comprei\s+", "", part).strip()

        m1 = pattern_qty_por.search(part)
        if m1:
            items.append({
                "produto": m1.group("prod").strip(),
                "quantidade": _to_float(m1.group("qtd"), default=1.0),
                "unidade": (m1.group("un") or "un").strip(),
                "valor": _to_float(m1.group("valor"), default=0.0),
            })
            continue

        m2 = pattern_prod_val.search(part)
        if m2:
            items.append({
                "produto": m2.group("prod").strip(),
                "quantidade": 1.0,
                "unidade": "un",
                "valor": _to_float(m2.group("valor"), default=0.0),
            })
    return _normalize_items(items)


def parse_compra_texto(shopper_id: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tool MCP:
    - Entrada: {"texto": "..."}
    - Saída: {"origem","texto_original","confidence","itens":[...]}
    """
    texto = str((args or {}).get("texto") or "").strip()
    itens = _parse_items(texto)
    if not itens and texto:
        itens = [{
            "produto": texto[:255],
            "quantidade": 1.0,
            "unidade": "un",
            "valor": 0.0,
        }]

    confidence = 0.85 if len(itens) > 1 else 0.7
    if itens and itens[0].get("valor", 0.0) == 0.0:
        confidence = min(confidence, 0.4)

    return {
        "ok": True,
        "shopper_id": shopper_id,
        "origem": "texto",
        "texto_original": texto,
        "confidence": confidence,
        "itens": itens,
    }

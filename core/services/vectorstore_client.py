"""
Cliente HTTP ao vectorstore_service (FastAPI + FAISS) para retrieval no fluxo cognitivo.
Reutiliza a mesma resolução de URL que `learning.order_feedback_service`.
"""
import json
import logging
import os
from typing import Any, Dict, List

import requests

logger = logging.getLogger(__name__)


def _vectorstore_url() -> str:
    explicit = os.getenv("VECTORSTORE_URL", "").strip()
    if explicit:
        return explicit.rstrip("/")
    port = os.getenv("VECTORSTORE_PORT", "8010").strip()
    return f"http://vectorstore_service:{port}"


def vectorstore_upsert(item_id: str, text: str) -> bool:
    """
    POST /upsert no vectorstore_service.
    Retorna True se gravado; False em falha (sem exceção — fluxo continua).
    """
    iid = (item_id or "").strip()
    body = (text or "").strip()
    if not iid or not body:
        return False
    url = f"{_vectorstore_url()}/upsert"
    try:
        timeout = float(os.getenv("VECTORSTORE_TIMEOUT", "10"))
        r = requests.post(url, json={"id": iid, "text": body}, timeout=timeout)
        r.raise_for_status()
        return True
    except Exception as e:
        logger.warning("vectorstore_upsert falhou: %s", e)
        return False


def vectorstore_search(
    query: str,
    k: int = 5,
    *,
    include_text: bool = True,
    id_prefix: str | None = None,
) -> List[Dict[str, Any]]:
    """
    POST /search no vectorstore_service.
    Retorna lista de {id, score, text?} ou [] se indisponível.
    Não levanta exceção em falha de rede — o fluxo principal continua.
    """
    q = (query or "").strip()
    if not q:
        return []
    url = f"{_vectorstore_url()}/search"
    try:
        timeout = float(os.getenv("VECTORSTORE_TIMEOUT", "10"))
        r = requests.post(
            url,
            json={"text": q, "k": k, "include_text": include_text},
            timeout=timeout,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results") or []
        if not isinstance(results, list):
            return []
        if id_prefix:
            p = str(id_prefix).strip()
            if p:
                results = [r for r in results if str((r or {}).get("id", "")).startswith(p)]
        return results
    except Exception as e:
        logger.warning("vectorstore_search falhou: %s", e)
        return []

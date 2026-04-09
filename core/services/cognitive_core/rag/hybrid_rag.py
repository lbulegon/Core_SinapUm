"""
Busca RAG em várias “camadas” via prefixo de `id` no vectorstore (FAISS não expõe namespace HTTP).

Convenção de IDs (extensível na ingestão):
- Global gastronomia (PDF SinapUm): ``sinapum.rag.gastronomia:<uuid>``
- Por tenant — conhecimento: ``tenant:{tenant_id}:gastro:...``
- Por tenant — operacional: ``tenant:{tenant_id}:operacional:...``

Sem documentos com esses prefixos, a camada devolve lista vazia (compatível).
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from core.services.vectorstore_client import vectorstore_search

logger = logging.getLogger(__name__)

# k elevado: o cliente filtra por prefixo *após* o top-k semântico global; aumenta hipótese de hits por camada.
_DEFAULT_K_FETCH = 80


def _sanitize_tenant_id(tenant_id: str) -> str:
    t = str(tenant_id or "").strip()
    if not t:
        return ""
    return re.sub(r"[^a-zA-Z0-9_.-]", "_", t)[:80]


def id_prefixes_for_tenant(tenant_id: str) -> Dict[str, str]:
    tid = _sanitize_tenant_id(tenant_id)
    if not tid:
        return {}
    return {
        "tenant": f"tenant:{tid}:gastro:",
        "operacional": f"tenant:{tid}:operacional:",
        "global": "sinapum.rag.gastronomia",
    }


def hybrid_rag_search(
    query: str,
    tenant_id: str,
    *,
    top_k_per_source: int = 5,
    fetch_k: int | None = None,
) -> List[Dict[str, Any]]:
    """
    Agrega resultados de várias camadas, etiquetados com ``source_type``.
    """
    q = (query or "").strip()
    if not q:
        return []

    k_fetch = int(fetch_k or max(_DEFAULT_K_FETCH, top_k_per_source * 15))
    k_fetch = max(10, min(200, k_fetch))

    out: List[Dict[str, Any]] = []
    seen: set[str] = set()

    tid = _sanitize_tenant_id(tenant_id)
    if tid:
        layers = id_prefixes_for_tenant(tid)
        for source_type, prefix in layers.items():
            hits = vectorstore_search(q, k=k_fetch, include_text=True, id_prefix=prefix)
            for h in hits or []:
                hid = str((h or {}).get("id", ""))
                if not hid or hid in seen:
                    continue
                seen.add(hid)
                row = dict(h)
                row["source_type"] = source_type
                out.append(row)
        return out

    # Sem tenant: só camada global alinhada ao ingestor actual
    hits = vectorstore_search(q, k=k_fetch, include_text=True, id_prefix="sinapum.rag.gastronomia")
    for h in hits or []:
        hid = str((h or {}).get("id", ""))
        if not hid or hid in seen:
            continue
        seen.add(hid)
        row = dict(h)
        row["source_type"] = "global"
        out.append(row)
    return out

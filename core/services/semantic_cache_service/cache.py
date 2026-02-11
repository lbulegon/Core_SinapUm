import os
import time
from typing import Any, Dict, Optional, Tuple

try:
    from redisvl.index import SearchIndex  # type: ignore
    from redisvl.schema import IndexSchema  # type: ignore
except Exception:
    SearchIndex = None
    IndexSchema = None

from .embeddings import embed_text, EmbeddingProviderError

_INDEX = None


def _enabled() -> bool:
    return os.getenv("SEMANTIC_CACHE_ENABLED", "false").lower() in ("1", "true", "yes")


def _get_index():
    global _INDEX
    if _INDEX is not None:
        return _INDEX

    if SearchIndex is None or IndexSchema is None:
        _INDEX = None
        return None

    index_name = os.getenv("REDISVL_INDEX_NAME", "vz_semantic_cache")
    prefix = os.getenv("REDISVL_PREFIX", "vz:cache")
    dim = int(os.getenv("SEMANTIC_VECTOR_DIM", "384"))

    schema_dict = {
        "index": {"name": index_name, "prefix": prefix, "storage_type": "hash"},
        "fields": [
            {"name": "intent", "type": "text"},
            {"name": "response", "type": "text"},
            {"name": "route", "type": "tag"},
            {"name": "channel", "type": "tag"},
            {"name": "user_id", "type": "tag"},
            {"name": "created_at", "type": "numeric"},
            {
                "name": "intent_vector",
                "type": "vector",
                "attrs": {
                    "dims": dim,
                    "distance_metric": "cosine",
                    "algorithm": "flat",
                    "datatype": "float32",
                },
            },
        ],
    }

    try:
        schema = IndexSchema.from_dict(schema_dict)
        index = SearchIndex(schema)
        index.create(overwrite=False)
        _INDEX = index
    except Exception:
        _INDEX = None
    return _INDEX


def _context_fields(context: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "route": str(context.get("route", "")),
        "channel": str(context.get("channel", "")),
        "user_id": str(context.get("user_id", "")),
    }


def semantic_query(intent: str, context: Dict[str, Any]) -> Optional[str]:
    if not _enabled():
        return None
    index = _get_index()
    if index is None:
        return None
    threshold = float(os.getenv("SEMANTIC_CACHE_THRESHOLD", "0.86"))
    k = int(os.getenv("SEMANTIC_CACHE_TOPK", "3"))
    try:
        vec = embed_text([intent])[0]
    except EmbeddingProviderError:
        return None
    try:
        results = index.query(
            vector=vec,
            vector_field_name="intent_vector",
            return_fields=["response", "intent", "route", "channel", "user_id"],
            num_results=k,
            filter_expression=None,
        )
    except Exception:
        return None
    best: Optional[Tuple[float, Dict[str, Any]]] = None
    for r in (results or []):
        score = float(r.get("score", 0.0)) if isinstance(r, dict) else 0.0
        doc = r.get("document", r) if isinstance(r, dict) else {}
        if best is None or score > best[0]:
            best = (score, doc)
    if not best:
        return None
    score, doc = best
    if score < threshold:
        return None
    return str(doc.get("response", "")) or None


def semantic_store(intent: str, context: Dict[str, Any], response: str, ttl_seconds: int = 3600) -> None:
    if not _enabled():
        return
    index = _get_index()
    if index is None:
        return
    try:
        vec = embed_text([intent])[0]
    except EmbeddingProviderError:
        return
    doc = {
        "intent": intent,
        "response": response,
        **_context_fields(context),
        "created_at": int(time.time()),
        "intent_vector": vec,
    }
    try:
        keys = index.load([doc])
        key = keys[0] if keys else None
        if key and ttl_seconds > 0 and getattr(index, "client", None):
            index.client.expire(key, ttl_seconds)
    except Exception:
        return

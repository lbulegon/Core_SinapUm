"""
Extração de PDF, chunking e upsert no vectorstore_service (JSON por chunk com metadados).
Usado pela UI RAG Gastronômico e pela tool MCP `core.rag_ingest`.
"""
from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Any, Callable, Dict, List, Optional, Sequence

from core.services.vectorstore_client import vectorstore_upsert

logger = logging.getLogger(__name__)

# (fase, percentual 0–100, detalhe opcional) — usado pela UI PRO e jobs assíncronos
ProgressCallback = Optional[Callable[[str, int, Optional[str]], None]]
ChunkProgressCallback = Optional[Callable[[int, int], None]]

DEFAULT_CHUNK_WORDS = 400
ID_PREFIX = "sinapum.rag.gastronomia"


def chunk_text_words(text: str, chunk_size: int = DEFAULT_CHUNK_WORDS) -> List[str]:
    words = (text or "").split()
    out: List[str] = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i : i + chunk_size]).strip()
        if chunk:
            out.append(chunk)
    return out


def classify_chunk_operational(text: str) -> Dict[str, str]:
    """
    Classificação para decisão operacional (MrFoo / RealityState).
    impacto_fluxo: alto → técnicas que sobrecarregam linha; médio → receitas; baixo → conceito.
    """
    t = (text or "").lower()
    if "ingredientes" in t or "modo de preparo" in t or "receita" in t:
        return {"type": "receita", "complexidade": "medio", "impacto_fluxo": "medio"}
    if (
        "emulsão" in t
        or "emulsao" in t
        or "redução" in t
        or "reducao" in t
        or "técnica" in t
        or "tecnica" in t
    ):
        return {"type": "tecnica", "complexidade": "alto", "impacto_fluxo": "alto"}
    return {"type": "conceito", "complexidade": "baixo", "impacto_fluxo": "baixo"}


def classify_chunk(text: str) -> str:
    return classify_chunk_operational(text)["type"]


def extract_pdf_chunks_only(
    file_path: str,
    *,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    max_chunks: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Só extração + chunking + classificação — sem vectorstore (preview UI).
    """
    if max_chunks is None:
        max_chunks = int(os.getenv("RAG_PREVIEW_MAX_CHUNKS", "500") or 500)
    try:
        import pdfplumber
    except ImportError:
        return {"ok": False, "error": "pdfplumber não instalado", "pages": 0, "chunks": [], "chunk_count": 0}

    full_text_parts: List[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    full_text_parts.append(t)
    except Exception as e:
        logger.exception("extract_pdf_chunks_only")
        return {"ok": False, "error": str(e), "pages": 0, "chunks": [], "chunk_count": 0}

    full_text = "\n\n".join(full_text_parts)
    if not full_text.strip():
        return {
            "ok": False,
            "error": "Nenhum texto extraído do PDF",
            "pages": 0,
            "chunks": [],
            "chunk_count": 0,
        }

    raw_chunks = chunk_text_words(full_text, chunk_size=chunk_words)
    truncated = False
    if len(raw_chunks) > max_chunks:
        raw_chunks = raw_chunks[:max_chunks]
        truncated = True

    chunks: List[Dict[str, str]] = []
    for c in raw_chunks:
        meta = classify_chunk_operational(c)
        chunks.append(
            {
                "text": c,
                "type": meta["type"],
                "complexidade": meta["complexidade"],
                "impacto_fluxo": meta["impacto_fluxo"],
            }
        )

    return {
        "ok": True,
        "pages": len(full_text_parts),
        "chunks": chunks,
        "chunk_count": len(chunks),
        "truncated": truncated,
    }


def ingest_chunk_strings(
    chunks: Sequence[str],
    *,
    source: str,
    domain: str = "gastronomia",
    id_prefix: str = ID_PREFIX,
    chunk_progress: ChunkProgressCallback = None,
) -> Dict[str, Any]:
    nonempty: List[str] = []
    for chunk in chunks:
        c = (chunk or "").strip()
        if c:
            nonempty.append(c)
    total = len(nonempty)
    ingested = 0
    errors: List[str] = []
    for idx, chunk in enumerate(nonempty):
        cid = f"{id_prefix}:{uuid.uuid4().hex}"
        meta = classify_chunk_operational(chunk)
        doc: Dict[str, Any] = {
            "domain": domain,
            "type": meta["type"],
            "complexidade": meta["complexidade"],
            "impacto_fluxo": meta["impacto_fluxo"],
            "source": source,
            "text": chunk,
        }
        payload = json.dumps(doc, ensure_ascii=False)
        if vectorstore_upsert(cid, payload):
            ingested += 1
        else:
            errors.append("upsert_failed")
        if chunk_progress and total > 0:
            chunk_progress(idx + 1, total)
    return {
        "chunks_ingested": ingested,
        "errors": errors,
    }


def ingest_text_as_chunks(
    full_text: str,
    *,
    source: str,
    domain: str = "gastronomia",
    id_prefix: str = ID_PREFIX,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    chunk_progress: ChunkProgressCallback = None,
) -> Dict[str, Any]:
    chunks = chunk_text_words(full_text, chunk_size=chunk_words)
    r = ingest_chunk_strings(
        chunks,
        source=source,
        domain=domain,
        id_prefix=id_prefix,
        chunk_progress=chunk_progress,
    )
    r["chunks_total"] = len(chunks)
    return r


def ingest_pdf_path(
    file_path: str,
    *,
    original_name: str = "",
    domain: str = "gastronomia",
    id_prefix: str = ID_PREFIX,
    chunk_words: int = DEFAULT_CHUNK_WORDS,
    progress_callback: ProgressCallback = None,
) -> Dict[str, Any]:
    def p(phase: str, pct: int, detail: Optional[str] = None) -> None:
        if progress_callback:
            progress_callback(phase, max(0, min(100, pct)), detail)

    try:
        import pdfplumber
    except ImportError:
        return {
            "ok": False,
            "error": "pdfplumber não instalado",
            "chunks_ingested": 0,
            "chunks_total": 0,
            "errors": [],
        }

    p("extracting", 18, "A abrir e ler o PDF")
    full_text_parts: List[str] = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    full_text_parts.append(t)
    except Exception as e:
        logger.exception("ingest_pdf_path")
        p("error", 0, str(e))
        return {
            "ok": False,
            "error": str(e),
            "chunks_ingested": 0,
            "chunks_total": 0,
            "errors": [str(e)],
        }

    p("extracting", 38, f"{len(full_text_parts)} página(s) com texto")
    full_text = "\n\n".join(full_text_parts)
    if not full_text.strip():
        p("error", 0, "Nenhum texto extraído")
        return {
            "ok": False,
            "error": "Nenhum texto extraído do PDF",
            "chunks_ingested": 0,
            "chunks_total": 0,
            "errors": [],
        }

    chunks_preview = chunk_text_words(full_text, chunk_size=chunk_words)
    p("chunking", 48, f"{len(chunks_preview)} chunk(s) preparados")

    src = original_name or file_path

    def on_chunk(cur: int, tot: int) -> None:
        if tot <= 0:
            return
        pct = 52 + int(43 * cur / tot)
        p("sending", min(96, pct), f"Enviando {cur}/{tot} ao vectorstore")

    r = ingest_text_as_chunks(
        full_text,
        source=src,
        domain=domain,
        id_prefix=id_prefix,
        chunk_words=chunk_words,
        chunk_progress=on_chunk,
    )
    r["ok"] = True
    r["pages"] = len(full_text_parts)
    p("sending", 98, f"{r.get('chunks_ingested', 0)} chunk(s) enviados")
    return r

import json
import logging
from typing import Any, Dict

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _format_cognitive_extras(context: Dict[str, Any]) -> str:
    parts = []
    rag = context.get("rag_results")
    if rag:
        lines = []
        for row in rag[:8]:
            rid = row.get("id", "")
            score = row.get("score", "")
            t = row.get("text")
            if t:
                preview = str(t)[:240].replace("\n", " ")
                lines.append(f"- id={rid} score={score} text_preview={preview!r}")
            else:
                lines.append(f"- id={rid} score={score}")
        parts.append("Trechos recuperados (RAG / ids):\n" + "\n".join(lines))
    riscos = context.get("riscos_previstos")
    if riscos:
        parts.append("Riscos previstos (heurístico):\n" + json.dumps(riscos, ensure_ascii=False))
    route = context.get("route")
    if route:
        parts.append(f"Rota de policy: {route}")
    reality = context.get("reality_slice")
    if reality and isinstance(reality, dict):
        parts.append("Fatiamento de realidade operacional (estruturado):\n" + json.dumps(reality, ensure_ascii=False)[:4000])
    hints = context.get("eoc_hints")
    if hints:
        parts.append("Hints EOC (enrich, não decisão):\n" + json.dumps(hints, ensure_ascii=False))
    return "\n\n".join(parts) if parts else ""


def llm_generate(
    prompt_input: str,
    context: Dict[str, Any],
    prompt_version: str,
    contract_version: str,
) -> str:
    """
    Geração via OpenMind (chat/completions) quando configurado; fallback seguro se indisponível.
    Assinatura pública inalterada para compatibilidade com o restante do Core.
    """
    base_url = getattr(settings, "OPENMIND_AI_URL", None) or getattr(settings, "OPENMIND_BASE_URL", "http://127.0.0.1:8001")
    base_url = str(base_url).rstrip("/")
    api_key = getattr(settings, "OPENMIND_AI_KEY", None) or getattr(settings, "OPENMIND_TOKEN", None) or ""

    cognitive_block = _format_cognitive_extras(context)
    system_parts = [
        "Você é o assistente do SinapUm. Responda de forma útil e concisa em português.",
        f"Versão de prompt: {prompt_version}. Contrato: {contract_version}.",
    ]
    if cognitive_block:
        system_parts.append(cognitive_block)
    system_content = "\n".join(system_parts)

    url = f"{base_url}/chat/completions"
    payload = {
        "model": getattr(settings, "OPENMIND_ORG_MODEL", "gpt-4o"),
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt_input or ""},
        ],
        "temperature": 0.4,
        "max_tokens": 1024,
    }
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        timeout = float(getattr(settings, "OPENMIND_TIMEOUT", 60))
        r = requests.post(url, json=payload, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        choices = data.get("choices") or []
        if choices:
            content = (choices[0].get("message") or {}).get("content")
            if content:
                return str(content).strip()
    except Exception as e:
        logger.warning("llm_generate OpenMind indisponível, usando fallback: %s", e)

    return (
        f"Entendi. Vou te ajudar com isso. (route={context.get('route')}, v={prompt_version})"
    )

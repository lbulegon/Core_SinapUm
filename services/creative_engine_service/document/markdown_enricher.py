"""
Enriquecimento de Markdown via OpenMind (IA).
Usado pelo fluxo md→PDF para melhorar o texto antes de gerar o PDF.
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Instruções padrão para o modelo
DEFAULT_INSTRUCTIONS = [
    "melhorar_ebook",
    "resumo_executivo",
    "revisar_pt",
]


def enrich_markdown_with_ai(
    markdown: str,
    instruction: str = "melhorar_ebook",
    custom_prompt: Optional[str] = None,
    max_tokens: int = 4096,
) -> Optional[str]:
    """
    Envia o Markdown para OpenMind.org (chat completions) para enriquecer o texto.

    Args:
        markdown: Conteúdo em Markdown.
        instruction: Uma das chaves em DEFAULT_INSTRUCTIONS ou texto livre.
        custom_prompt: Se informado, sobrescreve a instrução (ex.: "Traduza para inglês").
        max_tokens: Limite de tokens na resposta.

    Returns:
        Markdown enriquecido ou None em caso de falha (usa fallback no chamador).
    """
    try:
        from django.conf import settings
        import requests
    except ImportError:
        logger.warning("Django ou requests não disponível para enriquecimento")
        return None

    base_url = getattr(settings, "OPENMIND_ORG_BASE_URL", "")
    api_key = getattr(settings, "OPENMIND_AI_KEY", "") or getattr(settings, "OPENMIND_ORG_API_KEY", "")
    model = getattr(settings, "OPENMIND_ORG_MODEL", "gpt-4o")

    if not api_key:
        logger.warning("OPENMIND_AI_KEY não configurada; enriquecimento desabilitado")
        return None

    url = f"{base_url.rstrip('/')}/chat/completions"

    system_prompts = {
        "melhorar_ebook": (
            "Você é um editor. Receba um texto em Markdown e devolva APENAS o Markdown melhorado, "
            "pronto para ser convertido em ebook/PDF: linguagem clara, parágrafos bem estruturados, "
            "sem comentários fora do Markdown. Mantenha a formatação Markdown (títulos, listas, negrito)."
        ),
        "resumo_executivo": (
            "Você é um editor. Receba um texto em Markdown. Adicione no início um bloco '## Resumo executivo' "
            "com 2-4 frases resumindo o conteúdo. Devolva APENAS o Markdown completo (resumo + texto original), "
            "sem comentários adicionais."
        ),
        "revisar_pt": (
            "Você é um revisor de português. Receba um texto em Markdown e devolva APENAS o Markdown "
            "corrigido (ortografia, concordância, clareza). Mantenha a formatação Markdown intacta."
        ),
    }

    system_content = system_prompts.get(instruction.strip().lower())
    if custom_prompt and custom_prompt.strip():
        system_content = custom_prompt.strip()
    elif not system_content:
        system_content = system_prompts["melhorar_ebook"]

    messages = [
        {"role": "system", "content": system_content},
        {"role": "user", "content": markdown},
    ]

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": max_tokens,
    }

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=90)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("Falha ao enriquecer Markdown com OpenMind: %s", e)
        return None

    try:
        content = (data.get("choices") or [{}])[0].get("message", {}).get("content", "")
        if content and isinstance(content, str):
            return content.strip()
    except (IndexError, KeyError, TypeError):
        pass
    return None

from typing import Any, Dict


def llm_generate(
    prompt_input: str,
    context: Dict[str, Any],
    prompt_version: str,
    contract_version: str,
) -> str:
    return f"Entendi. Vou te ajudar com isso. (route={context.get('route')}, v={prompt_version})"

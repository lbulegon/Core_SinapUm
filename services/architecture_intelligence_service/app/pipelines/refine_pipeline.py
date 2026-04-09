"""
Refine Pipeline - Etapa refine do ciclo arquitetural.

Monta contexto -> seleciona prompt -> chama LLMAdapter -> retorna output.
"""
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

PROMPT_FILE = "app/prompts/refine_from_arb.md"


def run_refine(llm_adapter, input_content: str, previous_outputs: Optional[dict] = None) -> str:
    """
    Executa pipeline refine.

    Args:
        llm_adapter: Adapter de LLM (OpenMind, etc.)
        input_content: Conteúdo de entrada
        previous_outputs: Outputs de etapas anteriores

    Returns:
        Output estruturado da etapa
    """
    prompt_path = Path(PROMPT_FILE)
    prompt_template = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else "Analise o conteúdo."
    context = f"Input:

{input_content}"
    if previous_outputs:
        context += f"

Contexto anterior:
{previous_outputs}"
    full_prompt = f"{prompt_template}

---

{context}"
    return llm_adapter.complete(full_prompt, role="refinement_engine")

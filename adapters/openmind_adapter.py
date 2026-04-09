"""
Adapter OpenMind — análise de imagens, chamadas LLM.
Delega para OpenMind Service (services/openmind_service) ou endpoints Core.
"""
from typing import Any, Dict, Optional

from .base import BaseAdapter


def analyze_image(image_url: str = "", image_base64: str = "", **kwargs: Any) -> Dict[str, Any]:
    """Analisa imagem via OpenMind. Stub até integrar com serviço existente."""
    # Chamar POST /api/v1/analyze-product-image ou MCP tool vitrinezap.analisar_produto
    return {"success": False, "error": "OpenMind adapter not implemented"}


class OpenMindAdapter(BaseAdapter):
    """Adapter para chamadas OpenMind (não expõe Resources sinap:// por padrão)."""

    def get(self, entity: str, id: Optional[str] = None, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

    def list(self, entity: str, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

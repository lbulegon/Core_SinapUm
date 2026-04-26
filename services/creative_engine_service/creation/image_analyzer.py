"""
ImageAnalyzer - Análise de imagens de produtos
Usa OpenMind quando disponível, fallback para análise básica
"""
import base64
import logging
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

_DEFAULT_ANALYZE_PROMPT = (
    "Analise esta imagem de produto e retorne nome, descrição, preço, cor, material, categoria."
)


class ImageAnalyzer:
    """
    Analisa imagens de produtos e extrai informações.
    Integra com OpenMind (analyze-product-image) quando disponível.
    """

    def __init__(self, openmind_url: Optional[str] = None):
        self.openmind_url = openmind_url

    def analyze(self, image_path: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Analisa imagem e retorna atributos do produto.

        Returns:
            {
                'product_type': str,
                'main_color': str,
                'secondary_colors': list,
                'material': str,
                'style': str,
                'details': list,
                'product_category': str,
                'target_audience': str,
                'description': str,
                'price_range_suggested': str
            }
        """
        try:
            result = self._analyze_via_openmind(image_path, image_url)
            if result:
                return self._normalize_analysis(result)
        except Exception as e:
            logger.warning(f"Análise OpenMind falhou, usando fallback: {e}")

        return self._fallback_analysis(image_path)

    def _analyze_via_openmind(self, image_path: str, image_url: Optional[str]) -> Optional[Dict[str, Any]]:
        """Chama OpenMind analyze-product-image via MCP (core.openmind_analyze_product_image) ou HTTP legado."""
        try:
            from django.conf import settings
            import requests

            use_mcp = getattr(settings, "CREATIVE_ENGINE_OPENMIND_VIA_MCP", True)
            if use_mcp and image_url and not (image_path and Path(image_path).exists()):
                from app_mcp_tool_registry.services import execute_tool

                r = execute_tool(
                    "core.openmind_analyze_product_image",
                    {
                        "image_url": image_url,
                        "prompt": _DEFAULT_ANALYZE_PROMPT,
                    },
                    request_id=str(uuid.uuid4()),
                    trace_id=str(uuid.uuid4()),
                )
                if r.get("ok") and r.get("output"):
                    out = r["output"]
                    if isinstance(out, dict) and out.get("success") and out.get("data"):
                        return out["data"]
                    if isinstance(out, dict):
                        return out
            elif use_mcp and image_path and Path(image_path).exists():
                from app_mcp_tool_registry.services import execute_tool

                with open(image_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")
                r = execute_tool(
                    "core.openmind_analyze_product_image",
                    {
                        "image_base64": b64,
                        "prompt": _DEFAULT_ANALYZE_PROMPT,
                    },
                    request_id=str(uuid.uuid4()),
                    trace_id=str(uuid.uuid4()),
                )
                if r.get("ok") and r.get("output"):
                    out = r["output"]
                    if isinstance(out, dict) and out.get("success") and out.get("data"):
                        return out["data"]
                    if isinstance(out, dict):
                        return out

            url = getattr(settings, "OPENMIND_BASE_URL", "http://localhost:8001")
            endpoint = f"{str(url).rstrip('/')}/api/v1/analyze-product-image"
            token = getattr(settings, "OPENMIND_TOKEN", "")
            headers = {}
            if token:
                headers["Authorization"] = f"Bearer {token}"
            if Path(image_path).exists():
                with open(image_path, "rb") as f:
                    files = {"image": (Path(image_path).name, f, "image/jpeg")}
                    data = {"prompt": _DEFAULT_ANALYZE_PROMPT}
                    resp = requests.post(endpoint, files=files, data=data, headers=headers, timeout=60)
            elif image_url:
                return None
            else:
                return None
            if resp.status_code == 200:
                result = resp.json()
                if result.get("success") and result.get("data"):
                    return result["data"]
                return result
        except ImportError:
            pass
        except Exception as e:
            logger.debug("OpenMind não disponível: %s", e)
        return None

    def _normalize_analysis(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normaliza resposta OpenMind (formato Évora/modelo.json) para formato padrão"""
        # Suporta formato produto_generico_catalogo ou raiz
        produto = raw.get('produto', raw.get('produto_generico_catalogo', raw))
        if isinstance(produto, dict):
            data = produto
        else:
            data = raw

        nome = data.get('nome', data.get('nome_produto', raw.get('nome', 'Produto')))
        descricao = data.get('descricao', data.get('description', ''))
        preco = data.get('preco', data.get('price', ''))
        cor = data.get('cor') or (data.get('caracteristicas', {}) or {}).get('cor', '')
        categoria = data.get('categoria', data.get('product_category', 'geral'))

        return {
            'product_type': (nome or 'Produto').split()[0] if nome else 'produto',
            'main_color': cor or data.get('main_color', ''),
            'secondary_colors': data.get('secondary_colors', []),
            'material': data.get('material', (data.get('caracteristicas', {}) or {}).get('material', '')),
            'style': data.get('estilo', data.get('style', 'casual')),
            'details': data.get('detalhes', data.get('details', [])),
            'product_category': categoria,
            'target_audience': data.get('target_audience', 'unisex'),
            'description': descricao or f"{nome} {preco}".strip() or 'Produto em destaque',
            'price_range_suggested': 'popular' if preco else 'médio',
        }

    def _fallback_analysis(self, image_path: str) -> Dict[str, Any]:
        """Análise básica quando OpenMind não está disponível"""
        return {
            'product_type': 'produto',
            'main_color': '',
            'secondary_colors': [],
            'material': '',
            'style': 'casual',
            'details': [],
            'product_category': 'geral',
            'target_audience': 'unisex',
            'description': 'Produto em análise',
            'price_range_suggested': 'médio',
        }

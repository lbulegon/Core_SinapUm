"""
Geração de imagens por IA a partir de descrição (e opcionalmente imagem modelo).
Integra com OpenAI DALL·E quando OPENAI_API_KEY está configurada.
Permite trocar o provedor via settings no futuro (ex.: OpenMind, Stability).
"""
import logging
import uuid
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def generate_image_from_prompt(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = "vivid",
    output_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera uma imagem a partir de uma descrição (texto) usando o provedor configurado.

    Args:
        prompt: Descrição da imagem desejada (em português ou inglês).
        size: Tamanho (1024x1024, 1024x1792, 1792x1024 para DALL-E 3).
        quality: "standard" ou "hd".
        style: "vivid" ou "natural".
        output_dir: Diretório para salvar a imagem; se None, usa MEDIA_ROOT/creative_images.

    Returns:
        (file_path, error_message). file_path é o caminho do arquivo salvo; em falha, error_message preenchido.
    """
    try:
        from django.conf import settings
    except ImportError:
        return None, "Django não disponível"

    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key or not api_key.strip():
        return None, "OPENAI_API_KEY não configurada. Configure para gerar imagens com DALL·E."

    try:
        from openai import OpenAI
        import requests
    except ImportError as e:
        return None, f"Dependência não instalada: {e}"

    client = OpenAI(api_key=api_key.strip())

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt.strip(),
            size=size,
            quality=quality,
            style=style,
            n=1,
        )
    except Exception as e:
        logger.warning("Falha ao gerar imagem com OpenAI: %s", e)
        return None, str(e)

    if not response.data or len(response.data) == 0:
        return None, "Resposta da API sem imagem"

    image_url = response.data[0].url
    if not image_url:
        return None, "URL da imagem não retornada"

    # Baixar e salvar localmente (URLs OpenAI expiram em ~1h)
    if output_dir is None:
        media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
        output_dir = media_root / "creative_images"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"gen_{uuid.uuid4().hex[:12]}.png"
    file_path = output_dir / filename

    try:
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        file_path.write_bytes(resp.content)
    except Exception as e:
        logger.warning("Falha ao baixar imagem gerada: %s", e)
        return None, f"Falha ao salvar imagem: {e}"

    return str(file_path), None


def generate_image_from_reference(
    image_path: str,
    prompt: str,
    output_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera uma nova imagem a partir de uma imagem modelo + descrição (edição/variação).
    Usa OpenAI Images Edits quando disponível.

    Args:
        image_path: Caminho do arquivo da imagem modelo.
        prompt: Instrução de como modificar ou o que gerar com base na imagem.
        output_dir: Diretório de saída.

    Returns:
        (file_path, error_message).
    """
    try:
        from django.conf import settings
        from openai import OpenAI
        import requests
    except ImportError as e:
        return None, f"Importação falhou: {e}"

    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key or not api_key.strip():
        return None, "OPENAI_API_KEY não configurada"

    path = Path(image_path)
    if not path.exists():
        return None, "Arquivo de imagem modelo não encontrado"

    client = OpenAI(api_key=api_key.strip())

    try:
        with open(path, "rb") as f:
            response = client.images.edit(
                model="dall-e-2",
                image=f,
                prompt=prompt.strip(),
                n=1,
                size="1024x1024",
            )
    except Exception as e:
        logger.warning("Falha ao editar imagem com OpenAI: %s", e)
        return None, str(e)

    if not response.data or len(response.data) == 0:
        return None, "Resposta da API sem imagem"

    image_url = response.data[0].url
    if output_dir is None:
        media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
        output_dir = media_root / "creative_images"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"edit_{uuid.uuid4().hex[:12]}.png"
    file_path = output_dir / filename

    try:
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        file_path.write_bytes(resp.content)
    except Exception as e:
        return None, f"Falha ao salvar imagem: {e}"

    return str(file_path), None

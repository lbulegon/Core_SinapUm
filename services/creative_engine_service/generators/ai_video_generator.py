"""
Geração de vídeos por IA a partir de descrição (texto).
Integra com OpenAI Sora (Videos API) quando OPENAI_API_KEY está configurada.
Geração é assíncrona: create → poll status → download MP4.
"""
import logging
import time
import uuid
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Tamanhos suportados pela API Sora (aspect ratio)
VIDEO_SIZES = [
    "1280x720",   # 16:9 landscape
    "1920x1080",  # 16:9 Full HD (melhor com sora-2-pro)
    "1080x1920",  # 9:16 vertical
    "720x1280",   # 9:16 vertical 720p
]
# Durações em segundos (modelo e tamanho podem limitar)
VIDEO_SECONDS = ["8", "16", "20"]
DEFAULT_MODEL = "sora-2"
DEFAULT_SIZE = "1280x720"
DEFAULT_SECONDS = "8"
POLL_INTERVAL = 10
MAX_POLL_WAIT = 600  # 10 min máximo esperando


def generate_video_from_prompt(
    prompt: str,
    model: str = DEFAULT_MODEL,
    size: str = DEFAULT_SIZE,
    seconds: str = DEFAULT_SECONDS,
    output_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Gera um vídeo a partir de uma descrição usando a API Sora (OpenAI).

    Fluxo: create job → poll até completed/failed → download_content → salva MP4.

    Args:
        prompt: Descrição do vídeo (cenário, câmera, ação, iluminação).
        model: "sora-2" (rápido) ou "sora-2-pro" (maior qualidade).
        size: Resolução, ex. "1280x720", "1920x1080", "1080x1920".
        seconds: Duração em segundos: "8", "16" ou "20".
        output_dir: Onde salvar o MP4; se None, usa MEDIA_ROOT/creative_videos.

    Returns:
        (file_path, error_message). file_path é o caminho do MP4; em falha, error_message.
    """
    try:
        from django.conf import settings
    except ImportError:
        return None, "Django não disponível"

    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key or not api_key.strip():
        return None, "OPENAI_API_KEY não configurada. Configure para gerar vídeos com Sora."

    try:
        from openai import OpenAI
    except ImportError as e:
        return None, f"Dependência não instalada: {e}"

    client = OpenAI(api_key=api_key.strip())
    prompt = (prompt or "").strip()
    if not prompt:
        return None, "O prompt não pode ser vazio."

    # Criar job de geração
    try:
        video = client.videos.create(
            model=model.strip() or DEFAULT_MODEL,
            prompt=prompt,
            size=size.strip() or DEFAULT_SIZE,
            seconds=seconds.strip() or DEFAULT_SECONDS,
        )
    except Exception as e:
        logger.warning("Falha ao iniciar geração de vídeo com Sora: %s", e)
        return None, str(e)

    video_id = getattr(video, "id", None)
    if not video_id:
        return None, "Resposta da API sem id do vídeo."

    # Poll até completed ou failed
    elapsed = 0
    while elapsed < MAX_POLL_WAIT:
        try:
            video = client.videos.retrieve(video_id)
        except Exception as e:
            logger.warning("Falha ao consultar status do vídeo %s: %s", video_id, e)
            return None, f"Erro ao consultar status: {e}"

        status = getattr(video, "status", "")
        if status == "completed":
            break
        if status == "failed":
            err = getattr(getattr(video, "error", None), "message", None) or "Geração do vídeo falhou."
            return None, err

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    if getattr(video, "status", "") != "completed":
        return None, "Tempo limite excedido aguardando a geração do vídeo."

    # Salvar diretório
    if output_dir is None:
        media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
        output_dir = media_root / "creative_videos"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"gen_{uuid.uuid4().hex[:12]}.mp4"

    # Download do MP4
    try:
        content = client.videos.download_content(video_id, variant="video")
        if hasattr(content, "write_to_file"):
            content.write_to_file(str(out_path))
        else:
            # Fallback: read() e escrever
            data = content.read() if hasattr(content, "read") else getattr(content, "content", None)
            if not data:
                return None, "Não foi possível obter o conteúdo do vídeo."
            out_path.write_bytes(data)
    except Exception as e:
        logger.warning("Falha ao baixar vídeo %s: %s", video_id, e)
        return None, f"Falha ao salvar vídeo: {e}"

    return str(out_path), None

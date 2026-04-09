"""
Geração de áudio (fala) a partir de texto via OpenAI Text-to-Speech (TTS).
Completa a matriz verbal → sonora junto com PDF, imagem e vídeo.
"""
import logging
import uuid
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Vozes TTS OpenAI (pt-BR funciona bem com várias vozes)
TTS_VOICES = ("alloy", "echo", "fable", "onyx", "nova", "shimmer")
TTS_MODELS = ("tts-1", "tts-1-hd")
# Limite prático da API (caracteres por requisição)
MAX_INPUT_CHARS = 4096
DEFAULT_MODEL = "tts-1-hd"
DEFAULT_VOICE = "nova"


def generate_speech_from_text(
    text: str,
    voice: str = DEFAULT_VOICE,
    model: str = DEFAULT_MODEL,
    speed: float = 1.0,
    output_dir: Optional[Path] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Converte texto em áudio MP3 (narração sintética de alta qualidade).

    Args:
        text: Texto a ser falado (português ou outro idioma).
        voice: alloy, echo, fable, onyx, nova, shimmer.
        model: tts-1 (rápido) ou tts-1-hd (melhor qualidade).
        speed: 0.25 a 4.0 (1.0 = normal).
        output_dir: Diretório de saída; padrão MEDIA_ROOT/creative_audio.

    Returns:
        (caminho_do_mp3, mensagem_de_erro).
    """
    try:
        from django.conf import settings
    except ImportError:
        return None, "Django não disponível"

    api_key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not api_key or not api_key.strip():
        return None, "OPENAI_API_KEY não configurada. Configure para gerar áudio com TTS."

    text = (text or "").strip()
    if not text:
        return None, "O texto para narração não pode ser vazio."

    if len(text) > MAX_INPUT_CHARS:
        return None, f"Texto muito longo (máx. {MAX_INPUT_CHARS} caracteres por geração)."

    voice = (voice or DEFAULT_VOICE).strip().lower()
    if voice not in TTS_VOICES:
        voice = DEFAULT_VOICE

    model = (model or DEFAULT_MODEL).strip()
    if model not in TTS_MODELS:
        model = DEFAULT_MODEL

    try:
        speed = float(speed)
    except (TypeError, ValueError):
        speed = 1.0
    speed = max(0.25, min(4.0, speed))

    try:
        from openai import OpenAI
    except ImportError as e:
        return None, f"Dependência não instalada: {e}"

    client = OpenAI(api_key=api_key.strip())

    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed,
        )
    except Exception as e:
        logger.warning("Falha ao gerar áudio TTS com OpenAI: %s", e)
        return None, str(e)

    if output_dir is None:
        media_root = Path(getattr(settings, "MEDIA_ROOT", "media"))
        output_dir = media_root / "creative_audio"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"speech_{uuid.uuid4().hex[:12]}.mp3"

    try:
        if hasattr(response, "stream_to_file"):
            response.stream_to_file(str(out_path))
        elif hasattr(response, "write_to_file"):
            response.write_to_file(str(out_path))
        else:
            content = getattr(response, "content", None)
            if content is None and hasattr(response, "read"):
                content = response.read()
            if not content:
                return None, "Resposta da API sem dados de áudio."
            out_path.write_bytes(content)
    except Exception as e:
        logger.warning("Falha ao salvar MP3: %s", e)
        return None, f"Falha ao salvar áudio: {e}"

    return str(out_path), None

# ============================================================================
# ETAPA 1 - Gestão de Mídia Avançada
# Generator de Vídeo para Creative Engine
# ============================================================================
# 
# Este módulo fornece funcionalidades para trabalhar com vídeos como ativo comercial.
# A IA pode SUGERIR o envio de vídeo quando detectar dúvidas sobre funcionamento/uso.
# O Shopper sempre CONFIRMA antes do envio.
# ============================================================================

from typing import List, Optional, Dict, Any
import re
import logging

logger = logging.getLogger(__name__)


def detect_video_platform(url: str) -> Optional[str]:
    """
    Detecta a plataforma de vídeo a partir da URL.
    
    Args:
        url: URL do vídeo
        
    Returns:
        Nome da plataforma ('youtube', 'instagram', 'vimeo', etc.) ou None
    """
    url_lower = url.lower()
    
    if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return 'youtube'
    elif 'instagram.com' in url_lower or 'reel' in url_lower:
        return 'instagram'
    elif 'vimeo.com' in url_lower:
        return 'vimeo'
    elif 'tiktok.com' in url_lower:
        return 'tiktok'
    elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
        return 'facebook'
    
    return None


def extract_video_id(url: str, platform: Optional[str] = None) -> Optional[str]:
    """
    Extrai o ID do vídeo a partir da URL.
    
    Args:
        url: URL do vídeo
        platform: Plataforma (opcional, será detectada se não fornecida)
        
    Returns:
        ID do vídeo ou None
    """
    if not platform:
        platform = detect_video_platform(url)
    
    if platform == 'youtube':
        # YouTube: https://youtube.com/watch?v=VIDEO_ID ou https://youtu.be/VIDEO_ID
        match = re.search(r'(?:v=|/)([a-zA-Z0-9_-]{11})', url)
        return match.group(1) if match else None
    elif platform == 'instagram':
        # Instagram: https://instagram.com/reel/VIDEO_ID/
        match = re.search(r'/reel/([a-zA-Z0-9_-]+)', url)
        return match.group(1) if match else None
    elif platform == 'vimeo':
        # Vimeo: https://vimeo.com/VIDEO_ID
        match = re.search(r'vimeo.com/(\d+)', url)
        return match.group(1) if match else None
    
    return None


def get_video_thumbnail(url: str, platform: Optional[str] = None) -> Optional[str]:
    """
    Gera URL de thumbnail para o vídeo.
    
    Args:
        url: URL do vídeo
        platform: Plataforma (opcional, será detectada se não fornecida)
        
    Returns:
        URL do thumbnail ou None
    """
    if not platform:
        platform = detect_video_platform(url)
    
    video_id = extract_video_id(url, platform)
    if not video_id:
        return None
    
    if platform == 'youtube':
        return f'https://img.youtube.com/vi/{video_id}/maxresdefault.jpg'
    elif platform == 'vimeo':
        # Vimeo requer API para thumbnail, retornar None por enquanto
        return None
    
    return None


def validate_video_url(url: str) -> bool:
    """
    Valida se a URL é de uma plataforma de vídeo suportada.
    
    Args:
        url: URL a validar
        
    Returns:
        True se a URL é válida, False caso contrário
    """
    platform = detect_video_platform(url)
    return platform is not None


def format_video_for_message(video_urls: List[str]) -> Dict[str, Any]:
    """
    Formata vídeos para envio em mensagem.
    
    Args:
        video_urls: Lista de URLs de vídeo
        
    Returns:
        Dicionário formatado com informações dos vídeos
    """
    videos = []
    for url in video_urls:
        if not validate_video_url(url):
            logger.warning(f"URL de vídeo inválida ignorada: {url}")
            continue
        
        platform = detect_video_platform(url)
        video_id = extract_video_id(url, platform)
        thumbnail = get_video_thumbnail(url, platform)
        
        videos.append({
            'url': url,
            'platform': platform,
            'video_id': video_id,
            'thumbnail_url': thumbnail
        })
    
    return {
        'videos': videos,
        'count': len(videos)
    }


def suggest_video_for_context(context: Dict[str, Any]) -> Optional[str]:
    """
    Sugere envio de vídeo baseado no contexto da conversa.
    
    REGRA: IA apenas SUGERE, Shopper sempre CONFIRMA.
    
    Args:
        context: Contexto da conversa (produto, dúvida do cliente, etc.)
        
    Returns:
        URL do vídeo sugerido ou None
    """
    # Esta função será usada pela IA para sugerir vídeos
    # A implementação completa dependerá da lógica de negócio específica
    
    product = context.get('product')
    if not product:
        return None
    
    video_urls = product.get('video_urls', [])
    if not video_urls:
        return None
    
    # Retornar o primeiro vídeo disponível
    # A IA pode escolher qual vídeo sugerir baseado no contexto da dúvida
    return video_urls[0] if video_urls else None


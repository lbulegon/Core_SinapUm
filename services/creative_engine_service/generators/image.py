"""
Gerador/Adaptador de imagens para criativos
"""
import logging
import os
from typing import Dict, Any, Optional, List
from services.creative_engine_service.contracts import CreativeContext

logger = logging.getLogger(__name__)


class ImageGenerator:
    """
    Gerencia imagens de criativos
    
    MVP: NÃO gera imagem por IA obrigatoriamente.
    - Suporta usar foto original
    - Aplica moldura leve opcional
    - Aplica overlay de preço/título opcional
    - Gera versões por canal (crop/resize)
    - Preserva versão raw original
    """
    
    def __init__(self, base_media_path: str = "/media"):
        """
        Args:
            base_media_path: Caminho base para mídia
        """
        self.base_media_path = base_media_path
    
    def get_image_url(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext,
        apply_frame: bool = False,
        apply_overlay: bool = False,
        overlay_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Retorna URL da imagem adaptada para o canal
        
        Args:
            product_data: Dados do produto
            context: Contexto de geração
            apply_frame: Aplicar moldura leve
            apply_overlay: Aplicar overlay de preço/título
            overlay_data: Dados para overlay (preço, título)
        
        Returns:
            URL da imagem (original ou adaptada)
        """
        # Obter imagem original do produto
        imagens = product_data.get("imagens", [])
        if not imagens:
            logger.warning(f"Produto {product_data.get('id')} sem imagens")
            return None
        
        # Usar primeira imagem
        image_filename = imagens[0] if isinstance(imagens, list) else imagens
        
        # Construir URL base
        base_url = f"{self.base_media_path}/{image_filename}"
        
        # MVP: Retornar imagem original
        # Em produção, aqui seria feita adaptação por canal:
        # - status: crop quadrado, resize 1080x1080
        # - group: resize 800x600
        # - private: manter original ou resize 1200x1200
        
        if apply_frame or apply_overlay:
            # Em produção, gerar versão com frame/overlay
            # Por enquanto, retornar original
            logger.info(f"Aplicando frame/overlay para {image_filename} (MVP: retornando original)")
        
        return base_url
    
    def get_channel_variants(
        self,
        product_data: Dict[str, Any],
        context: CreativeContext
    ) -> Dict[str, Optional[str]]:
        """
        Retorna URLs de imagens adaptadas para cada canal
        
        Args:
            product_data: Dados do produto
            context: Contexto de geração
        
        Returns:
            Dict com image_url_status, image_url_group, image_url_private
        """
        base_url = self.get_image_url(product_data, context)
        
        # MVP: Retornar mesma imagem para todos os canais
        # Em produção, gerar variantes específicas
        return {
            "image_url_status": base_url,
            "image_url_group": base_url,
            "image_url_private": base_url,
        }
    
    def preserve_raw_image(self, image_url: str) -> str:
        """
        Preserva versão raw da imagem (não modifica original)
        
        Args:
            image_url: URL da imagem
        
        Returns:
            URL da imagem raw preservada
        """
        # MVP: Retornar URL original
        # Em produção, copiar para diretório raw/
        return image_url

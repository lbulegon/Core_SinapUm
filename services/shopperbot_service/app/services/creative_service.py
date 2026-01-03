"""Serviço de geração de cards criativos"""
import requests
from io import BytesIO
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from app.schemas.creative import CardRequest, CardResponse
from app.storage.catalog import CatalogStorage
from app.utils.config import CARDS_PATH
from app.utils.logging import logger


class CreativeService:
    """Gera cards de produtos preservando foto original"""
    
    def __init__(self, catalog_storage: CatalogStorage):
        self.catalog_storage = catalog_storage
    
    def generate_card(self, request: CardRequest) -> CardResponse:
        """Gera card do produto"""
        # Buscar produto no catálogo
        product = self.catalog_storage.get_product(request.product_id)
        
        if not product:
            raise ValueError(f"Produto {request.product_id} não encontrado")
        
        # Obter URL da imagem
        imagem_url = request.imagem_original_url
        if not imagem_url:
            # Buscar do catálogo
            imagens = product.get("imagens", [])
            if imagens:
                imagem_url = next(
                    (img["url"] for img in imagens if img.get("is_primary")),
                    imagens[0]["url"] if imagens else None
                )
        
        if not imagem_url:
            raise ValueError(f"Imagem não encontrada para produto {request.product_id}")
        
        # Baixar imagem
        try:
            response = requests.get(imagem_url, timeout=10)
            response.raise_for_status()
            image_data = BytesIO(response.content)
            base_image = Image.open(image_data)
            base_image = base_image.convert("RGB")
        except Exception as e:
            logger.error(f"Erro ao baixar imagem: {e}")
            raise ValueError(f"Erro ao processar imagem: {e}")
        
        # Adicionar overlays
        card_image = self._add_overlays(base_image, request.overlay)
        
        # Salvar card
        card_filename = f"{request.product_id}_{hash(request.overlay.nome)}.png"
        card_path = CARDS_PATH / card_filename
        card_image.save(card_path, "PNG", quality=95)
        
        # Retornar URL (relativa para servir via endpoint estático)
        card_url = f"/media/cards/{card_filename}"
        
        return CardResponse(
            card_url=card_url,
            product_id=request.product_id,
            format="png",
            width=card_image.width,
            height=card_image.height
        )
    
    def _add_overlays(self, base_image: Image.Image, overlay_data) -> Image.Image:
        """Adiciona overlays discretos na imagem"""
        # Redimensionar se necessário (mantém proporção)
        max_width = 800
        max_height = 800
        
        if base_image.width > max_width or base_image.height > max_height:
            base_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Criar cópia para editar
        card = base_image.copy()
        draw = ImageDraw.Draw(card)
        
        # Tentar carregar fonte (fallback para default se não disponível)
        try:
            # Tentar fontes comuns
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
            font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            # Fallback para fonte padrão
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Cor de destaque
        accent_color = overlay_data.cor_destaque or "#667eea"
        
        # Adicionar overlay semi-transparente na parte inferior
        overlay_height = 180
        overlay = Image.new("RGBA", (card.width, overlay_height), (0, 0, 0, 180))
        card.paste(overlay, (0, card.height - overlay_height), overlay)
        
        # Nome do produto (branco, bold)
        nome_y = card.height - overlay_height + 20
        draw.text((20, nome_y), overlay_data.nome, fill="white", font=font_large)
        
        # Preço (destaque, bold)
        preco_text = f"R$ {overlay_data.preco:.2f}"
        preco_y = nome_y + 45
        draw.text((20, preco_y), preco_text, fill=accent_color, font=font_large)
        
        # Promoção (se houver)
        if overlay_data.promo:
            promo_y = preco_y + 40
            draw.text((20, promo_y), overlay_data.promo, fill="#FFD700", font=font_medium)
        
        # CTA (botão no canto direito)
        cta_text = overlay_data.cta
        cta_bbox = draw.textbbox((0, 0), cta_text, font=font_medium)
        cta_width = cta_bbox[2] - cta_bbox[0] + 30
        cta_height = cta_bbox[3] - cta_bbox[1] + 15
        cta_x = card.width - cta_width - 20
        cta_y = card.height - overlay_height + (overlay_height - cta_height) // 2
        
        # Desenhar botão CTA
        draw.rectangle(
            [cta_x, cta_y, cta_x + cta_width, cta_y + cta_height],
            fill=accent_color,
            outline=None
        )
        cta_text_x = cta_x + 15
        cta_text_y = cta_y + (cta_height - (cta_bbox[3] - cta_bbox[1])) // 2
        draw.text((cta_text_x, cta_text_y), cta_text, fill="white", font=font_medium)
        
        return card


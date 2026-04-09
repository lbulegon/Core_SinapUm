"""
BackgroundRemovalService - Remoção de fundo de imagens de produtos
Usa rembg quando disponível, senão retorna imagem original
"""
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

REMBG_AVAILABLE = False
try:
    import rembg
    from PIL import Image
    REMBG_AVAILABLE = True
except ImportError:
    pass


class BackgroundRemovalService:
    """
    Remove fundo de imagens de produtos.
    Opcional: requer pip install rembg pillow
    """

    def __init__(self):
        self._session = None
        if REMBG_AVAILABLE:
            try:
                self._session = rembg.new_session()
            except Exception as e:
                logger.warning(f"rembg session falhou: {e}")
                self._session = None

    def remove_background(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """
        Remove fundo da imagem.

        Returns:
            Caminho da imagem com fundo removido, ou None se falhar
        """
        if not REMBG_AVAILABLE or not self._session:
            logger.debug("rembg não disponível - retornando imagem original")
            return image_path

        try:
            path = Path(image_path)
            if not path.exists():
                return None

            with open(path, 'rb') as f:
                input_data = f.read()

            output_data = rembg.remove(input_data, session=self._session)

            out_path = output_path or str(path.parent / f"{path.stem}_nobg{path.suffix}")
            with open(out_path, 'wb') as f:
                f.write(output_data)

            return out_path
        except Exception as e:
            logger.warning(f"Erro ao remover fundo: {e}")
            return image_path

    def extract_product_only(self, image_path: str) -> Optional[str]:
        """
        Extrai apenas o produto (remove fundo e faz crop).
        MVP: apenas remove fundo.
        """
        return self.remove_background(image_path)

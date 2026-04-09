"""
CreativeJobProcessor - Processa jobs de criação em background (fluxo Kwai/Tamo)
"""
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class CreativeJobProcessor:
    """
    Processa job de criação: análise → remoção de fundo → geração de variantes.
    MVP: Gera clean product (com/sem BG) e registra placeholders para lifestyle.
    """

    def __init__(self, media_base: str = "media/creative_outputs"):
        self.media_base = media_base
        self.analyzer = None
        self.bg_remover = None
        self.scene_lib = None

    def _get_analyzer(self):
        if self.analyzer is None:
            from .image_analyzer import ImageAnalyzer
            self.analyzer = ImageAnalyzer()
        return self.analyzer

    def _get_bg_remover(self):
        if self.bg_remover is None:
            from .background_removal import BackgroundRemovalService
            self.bg_remover = BackgroundRemovalService()
        return self.bg_remover

    def _get_scene_lib(self):
        if self.scene_lib is None:
            from .scene_templates import SceneTemplateLibrary
            self.scene_lib = SceneTemplateLibrary()
        return self.scene_lib

    def process(
        self,
        job_id: str,
        image_path: str,
        update_status_callback,
        base_url: str = "",
    ) -> List[Dict[str, Any]]:
        """
        Processa job completo.

        Args:
            job_id: ID do job
            image_path: Caminho da imagem de entrada
            update_status_callback: Função(job_id, status, stage, progress, description, error)
            base_url: URL base para montar URLs das imagens geradas

        Returns:
            Lista de outputs: [{'style': str, 'image_url': str, 'template_id': str}, ...]
        """
        outputs = []
        path = Path(image_path)

        if not path.exists():
            update_status_callback(job_id, 'failed', 'error', 0, '', f'Imagem não encontrada: {image_path}')
            return outputs

        try:
            # 1. Análise
            update_status_callback(job_id, 'processing', 'analyzing', 10, 'Analisando imagem...', None)
            analyzer = self._get_analyzer()
            analysis = analyzer.analyze(image_path)
            description = analysis.get('description', 'Produto em destaque')
            update_status_callback(job_id, 'processing', 'analyzing', 25, description, None)

            # 2. Remoção de fundo
            update_status_callback(job_id, 'processing', 'removing_bg', 35, 'Removendo fundo...', None)
            bg_remover = self._get_bg_remover()
            no_bg_path = bg_remover.remove_background(image_path)
            if no_bg_path and no_bg_path != image_path:
                product_image_path = no_bg_path
            else:
                product_image_path = image_path

            # 3. Geração de variantes
            update_status_callback(job_id, 'processing', 'generating', 50, 'Gerando variações...', None)
            scene_lib = self._get_scene_lib()
            templates = scene_lib.get_recommended(analysis)

            # Output 1: Clean product (sempre)
            clean_url = self._save_output(product_image_path, job_id, 'clean_product', base_url)
            if clean_url:
                outputs.append({
                    'style': 'clean_product',
                    'template_id': 'minimal_studio',
                    'image_url': clean_url,
                    'thumbnail_url': clean_url,
                })

            # Output 2: Original (ou no-bg como alternativa)
            orig_url = self._save_output(image_path, job_id, 'original', base_url)
            if orig_url and orig_url != clean_url:
                outputs.append({
                    'style': 'original',
                    'template_id': '',
                    'image_url': orig_url,
                    'thumbnail_url': orig_url,
                })

            # Output 3+: Placeholders para lifestyle (MVP - em produção seria IA)
            for i, template in enumerate(templates[:2]):
                if template.get('id') == 'minimal_studio':
                    continue
                # MVP: usar clean como placeholder para lifestyle
                placeholder_url = clean_url or orig_url
                if placeholder_url:
                    outputs.append({
                        'style': f"lifestyle_{template.get('id', i)}",
                        'template_id': template.get('id', ''),
                        'image_url': placeholder_url,
                        'thumbnail_url': placeholder_url,
                        'metadata': {'template': template.get('name'), 'mvp_placeholder': True},
                    })

            update_status_callback(job_id, 'completed', 'done', 100, description, None)
            return outputs

        except Exception as e:
            logger.exception(f"Erro ao processar job {job_id}")
            update_status_callback(job_id, 'failed', 'error', 0, '', str(e))
            return outputs

    def _save_output(self, image_path: str, job_id: str, style: str, base_url: str) -> Optional[str]:
        """Salva output e retorna URL (compatível com Django MEDIA_URL)"""
        try:
            path = Path(image_path)
            if not path.exists():
                return None

            out_dir = Path(self.media_base) / job_id
            out_dir.mkdir(parents=True, exist_ok=True)
            ext = path.suffix or '.png'
            out_name = f"{style}{ext}"
            out_path = out_dir / out_name

            import shutil
            shutil.copy2(path, out_path)

            # URL: /media/creative_outputs/job_id/style.png
            rel = f"creative_outputs/{job_id}/{out_name}"
            media_url = "/media/"
            if base_url:
                return f"{base_url.rstrip('/')}{media_url}{rel}"
            return f"{media_url}{rel}"
        except Exception as e:
            logger.warning(f"Erro ao salvar output: {e}")
            return None

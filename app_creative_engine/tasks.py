"""
Celery tasks do Creative Engine - processamento assíncrono de jobs
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


def _update_job_status(job_id, status, stage='', progress=0, description='', error=None):
    """Atualiza status do job no banco"""
    try:
        from app_creative_engine.models import CreativeJob
        job = CreativeJob.objects.get(id=job_id)
        job.status = status
        if stage:
            job.stage = stage
        if progress >= 0:
            job.progress = progress
        if description:
            job.description = description
        if error:
            job.error_message = error
        if status == 'completed':
            job.completed_at = timezone.now()
        job.save()
    except Exception as e:
        logger.warning(f"Erro ao atualizar job {job_id}: {e}")


@shared_task(bind=True)
def process_creative_job(self, job_id: str):
    """
    Processa job de criação em background.
    Enfileirado quando usuário envia foto.
    """
    try:
        from app_creative_engine.models import CreativeJob, CreativeJobOutput
        from django.conf import settings
        from services.creative_engine_service.creation import CreativeJobProcessor

        job = CreativeJob.objects.get(id=job_id)
        if job.status not in ('queued', 'processing'):
            logger.info(f"Job {job_id} já processado: {job.status}")
            return str(job_id)

        job.status = 'processing'
        job.save()

        base_url = getattr(settings, 'SINAPUM_CORE_BASE_URL', '') or ''
        base_dir = Path(getattr(settings, 'BASE_DIR', '.'))
        media_root = Path(getattr(settings, 'MEDIA_ROOT', 'media'))
        if not media_root.is_absolute():
            media_root = base_dir / media_root
        media_base = str(media_root / 'creative_outputs')

        # Resolver path da imagem (pode ser relativo a BASE_DIR ou absoluto)
        from pathlib import Path
        img_path = job.image_path
        if not Path(img_path).is_absolute():
            img_path = str(Path(base_dir) / img_path) if base_dir else img_path

        processor = CreativeJobProcessor(media_base=media_base)
        outputs = processor.process(
            job_id=str(job_id),
            image_path=img_path,
            update_status_callback=_update_job_status,
            base_url=base_url,
        )

        for out in outputs:
            CreativeJobOutput.objects.create(
                job=job,
                style=out.get('style', ''),
                template_id=out.get('template_id', ''),
                image_url=out.get('image_url', ''),
                thumbnail_url=out.get('thumbnail_url'),
                metadata=out.get('metadata', {}),
            )

        _update_job_status(str(job_id), 'completed', 'done', 100, job.description, None)
        return str(job_id)

    except Exception as e:
        if 'DoesNotExist' in type(e).__name__:
            logger.error(f"Job {job_id} não encontrado")
        else:
            logger.exception(f"Erro ao processar job {job_id}")
            _update_job_status(str(job_id), 'failed', 'error', 0, '', str(e))
        raise

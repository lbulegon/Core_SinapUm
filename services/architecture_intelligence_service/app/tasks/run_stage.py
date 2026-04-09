"""Task: executar uma etapa do ciclo arquitetural."""
import logging
from typing import Optional

from app.core.service import ArchitectureIntelligenceService
from app.core.models import ArchitectureStageRun

logger = logging.getLogger(__name__)


def run_stage(
    cycle_id: str,
    stage: str,
    input_content: Optional[str] = None,
    service: Optional[ArchitectureIntelligenceService] = None,
) -> ArchitectureStageRun:
    """
    Executa uma etapa específica de um ciclo.

    Args:
        cycle_id: ID do ciclo
        stage: Nome da etapa (design, review, refine, think, evolve, govern, stress)
        input_content: Conteúdo de entrada (usa artefato do ciclo se omitido)
        service: Instância do serviço (cria nova se não informada)

    Returns:
        Resultado da execução da etapa
    """
    svc = service or ArchitectureIntelligenceService()
    logger.info("Running stage %s for cycle %s", stage, cycle_id)
    return svc.run_stage(cycle_id, stage, input_content)

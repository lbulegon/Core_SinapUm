"""Task: gerar relatório de ciclo arquitetural."""
import logging
from typing import Optional

from app.core.service import ArchitectureIntelligenceService

logger = logging.getLogger(__name__)


def generate_report(
    cycle_id: str,
    service: Optional[ArchitectureIntelligenceService] = None,
) -> dict:
    """
    Gera relatório consolidado de um ciclo.

    Args:
        cycle_id: ID do ciclo
        service: Instância do serviço (cria nova se não informada)

    Returns:
        Dicionário com cycle_id, state, stage_runs, etc.
    """
    svc = service or ArchitectureIntelligenceService()
    logger.info("Generating report for cycle %s", cycle_id)
    return svc.get_cycle_report(cycle_id)

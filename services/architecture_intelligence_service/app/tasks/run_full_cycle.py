"""Task: executar ciclo arquitetural completo."""
import logging
from typing import Optional

from app.core.service import ArchitectureIntelligenceService
from app.core.models import ArchitectureCycle

logger = logging.getLogger(__name__)


def run_full_cycle(
    artifact_content: str,
    cycle_type: str = "full_cycle",
    trace_id: Optional[str] = None,
    service: Optional[ArchitectureIntelligenceService] = None,
) -> ArchitectureCycle:
    """
    Inicia um ciclo e executa todas as etapas até conclusão.

    Args:
        artifact_content: Conteúdo do artefato de entrada
        cycle_type: Tipo do ciclo (full_cycle, design_cycle, etc.)
        trace_id: ID de rastreamento opcional
        service: Instância do serviço (cria nova se não informada)

    Returns:
        Ciclo concluído
    """
    svc = service or ArchitectureIntelligenceService()
    cycle = svc.start_architecture_cycle(artifact_content, cycle_type, trace_id)
    logger.info("Cycle %s started, running full cycle", cycle.id)
    return svc.orchestrator.run_full_cycle(cycle.id)

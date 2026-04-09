"""Rotas da API - Architecture Intelligence."""
import logging
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Query

from app.api.schemas import StartCycleRequest, RunStageRequest, EvaluateRequest
from app.core.service import ArchitectureIntelligenceService
from app.adapters.llm_adapter import get_llm_adapter

logger = logging.getLogger(__name__)
router = APIRouter()

_svc = ArchitectureIntelligenceService()

def _trace_id(ctx):
    return ctx.meta.trace_id if ctx and ctx.meta else None


@router.post("/evaluate")
async def evaluate_architecture(req: EvaluateRequest):
    """
    Avalia um documento de arquitetura usando o pipeline completo:
    Design -> Review -> Refine -> Think -> Evolve -> Govern -> Stress
    -> Grand Jury -> Supreme Council
    """
    try:
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "architecture_intelligence_engine.md"
        if not prompt_path.exists():
            raise HTTPException(status_code=500, detail="Prompt file not found")
        template = prompt_path.read_text(encoding="utf-8")
        full_prompt = template + "\n\n## DOCUMENTO A AVALIAR:\n\n" + req.document
        provider = os.getenv("AIS_LLM_PROVIDER", "openmind")
        llm = get_llm_adapter(provider)
        result = llm.complete(full_prompt, system_prompt="Voce e o SinapUm Architecture Intelligence Engine.")
        return {"evaluation": result, "trace_id": req.trace_id}
    except Exception as e:
        logger.exception("evaluate_architecture failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cycle/start")
async def start_cycle(req: StartCycleRequest):
    """Inicia um novo ciclo arquitetural."""
    try:
        cycle = _svc.start_architecture_cycle(
            artifact_content=req.artifact_content,
            cycle_type=req.cycle_type,
            trace_id=_trace_id(req.context_pack),
        )
        return {
            "cycle_id": cycle.id,
            "cycle_type": cycle.cycle_type,
            "state": cycle.state,
            "trace_id": cycle.trace_id,
        }
    except Exception as e:
        logger.exception("start_cycle failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cycle/{cycle_id}/run_stage")
async def run_stage(cycle_id: str, stage: str = Query(..., description="design|review|refine|think|evolve|govern|stress"), req: RunStageRequest = None):
    """Executa uma etapa isolada."""
    try:
        run = _svc.run_stage(cycle_id, stage, req.input_content if req else None)
        return {
            "run_id": run.id,
            "stage": run.stage,
            "state": run.state,
            "output_preview": run.output_content[:500] + "..." if len(run.output_content) > 500 else run.output_content,
        }
    except Exception as e:
        logger.exception("run_stage failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cycle/{cycle_id}/report")
async def get_cycle_report(cycle_id: str):
    """Retorna relatório consolidado do ciclo."""
    try:
        return _svc.get_cycle_report(cycle_id)
    except Exception as e:
        logger.exception("get_cycle_report failed")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cycle/{cycle_id}/stages")
async def list_stage_runs(cycle_id: str):
    """Lista execuções de etapas do ciclo."""
    try:
        runs = _svc.list_stage_runs(cycle_id)
        return {"stages": [{"run_id": r.id, "stage": r.stage, "state": r.state} for r in runs]}
    except Exception as e:
        logger.exception("list_stage_runs failed")
        raise HTTPException(status_code=500, detail=str(e))

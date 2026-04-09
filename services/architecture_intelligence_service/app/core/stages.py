"""Stage executor."""
from datetime import datetime
from pathlib import Path
from typing import Optional
from .enums import ArchitectureStage, STAGE_TO_ROLE
from .exceptions import StageExecutionError
from .models import ArchitectureStageRun
from app.adapters.llm_adapter import LLMAdapter

class StageExecutor:
    def __init__(self, llm: LLMAdapter, prompts_dir: str = "app/prompts"):
        self.llm = llm
        self.prompts_dir = Path(prompts_dir)

    def _load_prompt(self, stage: ArchitectureStage) -> str:
        f = self.prompts_dir / f"{STAGE_TO_ROLE.get(stage, stage.value)}.md"
        if f.exists():
            return f.read_text(encoding="utf-8")
        return f"Você é especialista em {stage.value}. Analise o conteúdo."

    def run(self, stage: ArchitectureStage, input_content: str, run_id: str, cycle_id: str, previous: Optional[dict] = None) -> ArchitectureStageRun:
        run = ArchitectureStageRun(id=run_id, cycle_id=cycle_id, stage=stage.value, state="running", input_content=input_content, started_at=datetime.utcnow())
        try:
            tpl = self._load_prompt(stage)
            ctx = f"Input:\n\n{input_content}"
            if previous:
                ctx += f"\n\nContexto anterior:\n{previous}"
            out = self.llm.complete(f"{tpl}\n\n---\n\n{ctx}", role=STAGE_TO_ROLE.get(stage, stage.value))
            run.output_content = out
            run.state = "completed"
            run.completed_at = datetime.utcnow()
        except Exception as e:
            run.state = "failed"
            run.error_message = str(e)
            run.completed_at = datetime.utcnow()
            raise StageExecutionError(f"Stage {stage.value} failed: {e}", stage=stage.value, cause=e)
        return run

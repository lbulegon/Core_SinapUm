"""Pydantic schemas."""
from typing import Optional
from pydantic import BaseModel, Field

class ContextPackMeta(BaseModel):
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: Optional[str] = None

class ContextPack(BaseModel):
    meta: Optional[ContextPackMeta] = None

class StartCycleRequest(BaseModel):
    artifact_content: str = Field(..., description="Conteúdo do artefato arquitetural")
    cycle_type: str = Field(default="full_cycle")
    context_pack: Optional[ContextPack] = None

class RunStageRequest(BaseModel):
    input_content: Optional[str] = None
    context_pack: Optional[ContextPack] = None

class CycleResponse(BaseModel):
    cycle_id: str
    cycle_type: str
    state: str
    trace_id: Optional[str] = None


class EvaluateRequest(BaseModel):
    document: str = Field(..., description="Documento de arquitetura a avaliar")
    trace_id: Optional[str] = None

"""Domain models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

@dataclass
class ArchitectureArtifact:
    content: str
    artifact_type: str = "document"
    metadata: Dict[str, Any] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ArchitectureCycle:
    id: str
    cycle_type: str
    state: str
    artifact: ArchitectureArtifact
    trace_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class ArchitectureStageRun:
    id: str
    cycle_id: str
    stage: str
    state: str
    input_content: str
    output_content: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

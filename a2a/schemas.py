"""
Schemas do plano A2A (intent, steps, expected_output).
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlanStep:
    id: str
    tool_name: str
    tool_version: Optional[str] = None
    args: Dict[str, Any] = field(default_factory=dict)
    resources: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    timeout_seconds: Optional[int] = None

    def to_mcp_payload(self) -> Dict[str, Any]:
        return {"tool": self.tool_name, "version": self.tool_version, "input": self.args}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "PlanStep":
        return cls(
            id=d.get("id", ""),
            tool_name=d.get("tool_name", ""),
            tool_version=d.get("tool_version"),
            args=d.get("args") or {},
            resources=d.get("resources") or [],
            depends_on=d.get("depends_on") or [],
            timeout_seconds=d.get("timeout_seconds"),
        )


@dataclass
class A2APlan:
    intent: str
    steps: List[PlanStep]
    expected_output: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent": self.intent,
            "steps": [
                {
                    "id": s.id,
                    "tool_name": s.tool_name,
                    "tool_version": s.tool_version,
                    "args": s.args,
                    "resources": s.resources,
                    "depends_on": s.depends_on,
                    "timeout_seconds": s.timeout_seconds,
                }
                for s in self.steps
            ],
            "expected_output": self.expected_output,
        }

    def to_acp_payload(self) -> Dict[str, Any]:
        return {
            "steps": [
                {
                    "tool": s.tool_name,
                    "version": s.tool_version,
                    "input": s.args,
                    "timeout_seconds": s.timeout_seconds,
                }
                for s in self.steps
            ],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "A2APlan":
        steps = [PlanStep.from_dict(s) for s in (d.get("steps") or [])]
        return cls(intent=d.get("intent", ""), steps=steps, expected_output=d.get("expected_output"))

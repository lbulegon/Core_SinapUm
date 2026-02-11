import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import requests


@dataclass
class PolicyDecision:
    route: str = "support"
    allow_ai: bool = True
    template_id: Optional[str] = None
    template_text: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    ttl_seconds: int = 3600
    policy_version: str = "v1"
    prompt_version: Optional[str] = "v1"


class EvoraMCPClientError(RuntimeError):
    pass


class EvoraMCPClient:
    """
    Cliente MCP para Evora.
    - Se pacote `mcp` existir e EVORA_MCP_* estiver configurado, usa MCP de verdade.
    - Caso contrário, mantém fallback seguro (não quebra o fluxo).
    """

    def __init__(self, timeout_seconds: int = 6, retries: int = 2):
        self.timeout_seconds = timeout_seconds
        self.retries = retries
        self.evora_mcp_url = os.getenv("EVORA_MCP_URL", "").strip()
        self.evora_mcp_token = os.getenv("EVORA_MCP_TOKEN", "").strip()
        self._mcp = None
        try:
            import mcp  # type: ignore
            self._mcp = mcp
        except Exception:
            self._mcp = None

    def _mcp_enabled(self) -> bool:
        return bool(self._mcp and self.evora_mcp_url)

    def policy_decide(
        self,
        event_id: str,
        channel: str,
        user_id: str,
        text: str,
        context_hint: Dict[str, Any],
        contract_version: str = "v1",
    ) -> PolicyDecision:
        if self._mcp_enabled():
            return self._policy_decide_mcp(
                event_id=event_id,
                channel=channel,
                user_id=user_id,
                text=text,
                context_hint=context_hint,
                contract_version=contract_version,
            )
        tags = []
        if context_hint and isinstance(context_hint, dict):
            raw_tags = context_hint.get("tags", [])
            if isinstance(raw_tags, list):
                tags = [str(t) for t in raw_tags]
        return PolicyDecision(
            route="support",
            allow_ai=True,
            template_id=None,
            template_text=None,
            tags=tags,
            ttl_seconds=3600,
            policy_version="v1",
            prompt_version="v1",
        )

    def domain_append_message(
        self,
        event_id: str,
        direction: str,
        message_text: str,
        metadata: Dict[str, Any],
        contract_version: str = "v1",
    ) -> bool:
        if self._mcp_enabled():
            return self._domain_append_message_mcp(
                event_id=event_id,
                direction=direction,
                message_text=message_text,
                metadata=metadata,
                contract_version=contract_version,
            )
        return True

    def _policy_decide_mcp(self, **kwargs: Any) -> PolicyDecision:
        last_err: Optional[Exception] = None
        for _ in range(self.retries + 1):
            try:
                data = self._call_tool("evora.policy.decide", kwargs)
                return PolicyDecision(
                    route=str(data.get("route", "support")),
                    allow_ai=bool(data.get("allow_ai", True)),
                    template_id=data.get("template_id"),
                    template_text=data.get("template_text"),
                    tags=list(data.get("tags", []) or []),
                    ttl_seconds=int(data.get("ttl_seconds", 3600)),
                    policy_version=str(data.get("policy_version", "v1")),
                    prompt_version=str(data.get("prompt_version", "v1")) if data.get("prompt_version") else "v1",
                )
            except Exception as e:
                last_err = e
                time.sleep(0.2)
        raise EvoraMCPClientError(f"policy_decide MCP failed: {last_err}")

    def _domain_append_message_mcp(self, **kwargs: Any) -> bool:
        last_err: Optional[Exception] = None
        for _ in range(self.retries + 1):
            try:
                data = self._call_tool("evora.domain.append_message", kwargs)
                return bool(data.get("success", True))
            except Exception as e:
                last_err = e
                time.sleep(0.2)
        raise EvoraMCPClientError(f"domain_append_message MCP failed: {last_err}")

    def _call_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.evora_mcp_url.rstrip('/')}/mcp/call"
        headers = {"Content-Type": "application/json"}
        if self.evora_mcp_token:
            headers["Authorization"] = f"Bearer {self.evora_mcp_token}"

        payload = {
            "tool": tool_name,
            "input": tool_input,
        }

        resp = requests.post(url, json=payload, headers=headers, timeout=self.timeout_seconds)
        if resp.status_code >= 400:
            raise EvoraMCPClientError(f"MCP HTTP {resp.status_code}: {resp.text[:500]}")

        try:
            data = resp.json()
        except Exception:
            raise EvoraMCPClientError("Resposta MCP não é JSON válido")

        return data.get("output", data)

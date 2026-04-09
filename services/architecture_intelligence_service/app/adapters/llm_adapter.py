"""LLM Adapter - OpenMind (Core) ou stub."""
import os
import requests
from abc import ABC, abstractmethod
from typing import Optional

OPENMIND_URL = os.getenv("OPENMIND_SERVICE_URL", "http://openmind:8001")

class LLMAdapter(ABC):
    @abstractmethod
    def complete(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        pass

class OpenMindAdapter(LLMAdapter):
    def complete(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        url = f"{OPENMIND_URL}/chat/completions"
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": kwargs.get("model", "gpt-4o"),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        try:
            headers = {}
            key = os.getenv("OPENMIND_AI_KEY", "")
            if key:
                headers["Authorization"] = f"Bearer {key}"
            r = requests.post(url, json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()
            if "choices" in data and data["choices"]:
                return data["choices"][0].get("message", {}).get("content", "")
            return str(data)
        except Exception as e:
            return f"[OpenMind error: {e}]"

class StubLLMAdapter(LLMAdapter):
    def complete(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        role = kwargs.get("role", "architect")
        return f"[STUB {role}] Processed ({len(prompt)} chars). Configure OpenMind."

def get_llm_adapter(provider: str = "openmind") -> LLMAdapter:
    if provider == "openmind":
        return OpenMindAdapter()
    return StubLLMAdapter()

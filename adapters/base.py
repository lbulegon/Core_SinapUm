"""Interface base para adapters."""
from abc import ABC
from typing import Any, Dict, Optional


class BaseAdapter(ABC):
    def get(self, entity: str, id: Optional[str] = None, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

    def list(self, entity: str, query: Optional[Dict[str, str]] = None) -> Optional[Dict[str, Any]]:
        return None

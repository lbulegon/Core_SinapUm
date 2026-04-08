"""
Command Engine — handlers plugáveis (sem ORM; execução com BD em services).
"""

from command_engine.executor import execute_pending
from command_engine.registry import CommandRegistry

__all__ = ["CommandRegistry", "execute_pending"]

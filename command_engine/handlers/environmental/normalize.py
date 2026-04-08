from __future__ import annotations

import logging
from typing import Any

from command_engine.base import BaseCommandHandler

logger = logging.getLogger(__name__)


class NormalizeHandler(BaseCommandHandler):
    command_name = "normalize"

    def execute(self, command: Any, context: dict[str, Any] | None) -> dict[str, Any]:
        logger.info("NormalizeHandler: normalizar operação (payload=%s)", getattr(command, "payload", None))
        return {"status": "normalized"}

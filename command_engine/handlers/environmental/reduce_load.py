from __future__ import annotations

import logging
from typing import Any

from command_engine.base import BaseCommandHandler

logger = logging.getLogger(__name__)


class ReduceLoadHandler(BaseCommandHandler):
    command_name = "reduce_load"

    def execute(self, command: Any, context: dict[str, Any] | None) -> dict[str, Any]:
        logger.info("ReduceLoadHandler: redução de carga (payload=%s)", getattr(command, "payload", None))
        return {"status": "reduced"}

from __future__ import annotations

import logging
from typing import Any

from command_engine.base import BaseCommandHandler

logger = logging.getLogger(__name__)


class PauseOrdersHandler(BaseCommandHandler):
    command_name = "pause_orders"

    def execute(self, command: Any, context: dict[str, Any] | None) -> dict[str, Any]:
        logger.info("PauseOrdersHandler: pausa de novos pedidos (payload=%s)", getattr(command, "payload", None))
        return {"status": "paused"}

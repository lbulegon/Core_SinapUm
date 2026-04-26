# ============================================================================
# ARQUITETURA NOVA - app_ai_bridge.services.openmind_service
# ============================================================================
# Service para comunicação com OpenMind — delegado ao dispatcher MCP
# (execute_tool core.openmind_process_inbound).
# ============================================================================

import logging
import uuid
from typing import Dict, Any, Optional

from django.conf import settings
from app_conversations.models import Conversation, Message

logger = logging.getLogger(__name__)

OPENMIND_INBOUND_MCP_TOOL = "core.openmind_process_inbound"


class OpenMindService:
    """
    Service para comunicação com OpenMind AI
    """

    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        """
        Inicializa cliente (base_url/token mantidos para compat. com chamadas directas
        se OPENMIND_INBOUND_MCP_TOOL for desactivado; o fluxo principal usa execute_tool).
        """
        self.base_url = base_url or getattr(
            settings, "OPENMIND_BASE_URL", "http://69.169.102.84:8001"
        )
        self.token = token or (
            getattr(settings, "OPENMIND_TOKEN", None)
            or getattr(settings, "OPENMIND_AI_KEY", None)
            or ""
        )

    def process_inbound(self, canonical_event: Dict[str, Any], conversation: Conversation) -> Optional[Dict[str, Any]]:
        """
        Processa evento canônico e retorna sugestão da IA (via tool MCP
        `core.openmind_process_inbound` → registo em ToolCallLog).
        """
        last_messages = Message.objects.filter(conversation=conversation).order_by("-timestamp")[:10]

        context: Dict[str, Any] = {
            "last_messages": [
                {
                    "direction": msg.direction,
                    "text": msg.text,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in last_messages
            ],
            "conversation": {
                "id": str(conversation.id),
                "customer_phone": conversation.customer_phone,
                "customer_name": conversation.customer_name,
                "mode": conversation.mode,
            },
        }

        input_data: Dict[str, Any] = {
            "event": canonical_event,
            "context": context,
        }
        use_mcp = getattr(settings, "OPENMIND_INBOUND_VIA_MCP", True)

        if not use_mcp:
            return self._process_inbound_direct(input_data)

        from app_mcp_tool_registry.services import execute_tool

        try:
            mcp = execute_tool(
                OPENMIND_INBOUND_MCP_TOOL,
                input_data,
                context_pack=None,
                request_id=str(uuid.uuid4()),
                trace_id=str(uuid.uuid4()),
            )
        except Exception as e:
            logger.error("Falha MCP %s: %s", OPENMIND_INBOUND_MCP_TOOL, e, exc_info=True)
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "suggested_reply": "Entendi. Vou te ajudar. O que você procura?",
                "actions": [],
            }

        if mcp.get("ok") and mcp.get("output"):
            return mcp["output"]
        logger.warning("OpenMind MCP retornou erro: %s", mcp.get("error"))
        return {
            "intent": "unknown",
            "confidence": 0.0,
            "suggested_reply": "Entendi. Vou te ajudar. O que você procura?",
            "actions": [],
        }

    def _process_inbound_direct(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Caminho legado HTTP directo (OPENMIND_INBOUND_VIA_MCP=False). Corpo = ProcessMessageRequest."""
        import requests

        from app_mcp_tool_registry.openmind_process_message import (
            build_process_message_request,
            map_process_message_response_to_bridge,
        )

        event = input_data.get("event") or {}
        context = input_data.get("context") or {}
        try:
            body = build_process_message_request(event, context)
        except ValueError as e:
            logger.error("openmind direct: %s", e)
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "suggested_reply": "Entendi. Vou te ajudar. O que você procura?",
                "actions": [],
            }

        url = f"{str(self.base_url).rstrip('/')}/api/v1/process-message"
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        timeout = int(getattr(settings, "OPENMIND_TIMEOUT", 30) or 30)
        try:
            r = requests.post(url, json=body, headers=headers, timeout=timeout)
            r.raise_for_status()
            result = r.json()
        except requests.RequestException as e:
            logger.error("Erro ao fazer requisição para OpenMind: %s", e)
            return {
                "intent": "unknown",
                "confidence": 0.0,
                "suggested_reply": "Entendi. Vou te ajudar. O que você procura?",
                "actions": [],
            }
        return map_process_message_response_to_bridge(result)

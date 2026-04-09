"""
Envio de comandos do Core para o MrFoo (aceitação 202 + fila Celery no destino).
"""

from __future__ import annotations

import logging
from typing import Any, Dict

import requests
from django.conf import settings

logger = logging.getLogger("core_dispatch")


def _command_url() -> str:
    explicit = (getattr(settings, "MRFOO_COMMAND_URL", None) or "").strip()
    if explicit:
        return explicit.rstrip("/")
    base = (getattr(settings, "MRFOO_BASE_URL", None) or "").strip().rstrip("/")
    path = (getattr(settings, "MRFOO_COMMAND_PATH", None) or "/api/integracoes/sinapum/command/").strip()
    if not path.startswith("/"):
        path = "/" + path
    if not base:
        return ""
    return f"{base}{path}"


def emitir_comando(comando: Dict[str, Any]) -> Dict[str, Any]:
    """
    POST JSON no MrFoo. Headers: X-SINAPUM-KEY (se configurado), Authorization Bearer (opcional).
    """
    url = _command_url()
    if not url:
        msg = "MRFOO_COMMAND_URL ou MRFOO_BASE_URL não configurados"
        logger.error(msg)
        return {"ok": False, "error": msg}

    headers: Dict[str, str] = {"Content-Type": "application/json"}
    key = (getattr(settings, "MRFOO_SINAPUM_OUTBOUND_KEY", None) or "").strip()
    if key:
        headers["X-SINAPUM-KEY"] = key
    bearer = (getattr(settings, "MRFOO_OUTBOUND_BEARER_TOKEN", None) or "").strip()
    if bearer:
        headers["Authorization"] = f"Bearer {bearer}"

    timeout = float(getattr(settings, "MRFOO_COMMAND_TIMEOUT_SECONDS", 10))

    try:
        response = requests.post(url, json=comando, headers=headers, timeout=timeout)
        payload: Dict[str, Any] = {
            "ok": response.status_code in (200, 202),
            "status_code": response.status_code,
            "comando": comando.get("comando"),
            "command_id": comando.get("command_id"),
        }
        try:
            payload["body"] = response.json() if response.content else {}
        except Exception:
            payload["body"] = {"text": (response.text or "")[:500]}

        logger.info(
            "comando_enviado",
            extra={
                "action": "comando_enviado",
                "comando": comando.get("comando"),
                "command_id": comando.get("command_id"),
                "status_code": response.status_code,
            },
        )
        return payload
    except requests.RequestException as e:
        logger.exception("Erro ao enviar comando ao MrFoo: %s", e)
        return {
            "ok": False,
            "error": str(e),
            "comando": comando.get("comando"),
            "command_id": comando.get("command_id"),
        }

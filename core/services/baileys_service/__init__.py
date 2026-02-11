"""
Baileys Service - Serviço WhatsApp usando Baileys (Python)
===========================================================

Serviço Python equivalente ao projeto Node.js bot-do-mago.
Implementa conexão WhatsApp, autenticação, envio e recebimento de mensagens.
"""

from .baileys_client import BaileysClient
from .exceptions import BaileysConnectionError, BaileysAuthError, BaileysMessageError

__all__ = [
    'BaileysClient',
    'BaileysConnectionError',
    'BaileysAuthError',
    'BaileysMessageError',
]

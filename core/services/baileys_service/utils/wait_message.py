"""
Wait Message - Baileys Service
===============================

Sistema de espera de resposta de mensagens.
Equivalente ao waitMessage.js do projeto Node.js.
"""
import asyncio
from typing import Optional, Dict, Callable
from datetime import datetime, timedelta


class WaitMessageManager:
    """
    Gerenciador de espera de respostas
    
    Permite esperar por uma resposta de um contato específico
    com timeout configurável.
    """
    
    def __init__(self):
        self._waiting_responses: Dict[str, asyncio.Future] = {}
    
    def _get_key(self, remote_jid: str, participant: Optional[str] = None) -> str:
        """Gera chave única para identificar espera"""
        if participant:
            return f"{remote_jid}:{participant}"
        return remote_jid
    
    async def wait_response(
        self,
        remote_jid: str,
        participant: Optional[str] = None,
        timeout: int = 30000  # milissegundos
    ) -> str:
        """
        Espera por uma resposta de um contato
        
        Args:
            remote_jid: JID do contato (ex: 5511999999999@s.whatsapp.net)
            participant: JID do participante (para grupos)
            timeout: Timeout em milissegundos
        
        Returns:
            Texto da resposta recebida
        
        Raises:
            asyncio.TimeoutError: Se timeout for atingido
        """
        key = self._get_key(remote_jid, participant)
        
        # Cria future para esperar resposta
        future = asyncio.Future()
        self._waiting_responses[key] = future
        
        try:
            # Espera resposta com timeout
            response = await asyncio.wait_for(
                future,
                timeout=timeout / 1000.0  # Converte para segundos
            )
            return response
        except asyncio.TimeoutError:
            # Remove do dicionário se ainda estiver lá
            self._waiting_responses.pop(key, None)
            raise asyncio.TimeoutError("⏱️ Tempo esgotado.")
        finally:
            # Limpa future
            self._waiting_responses.pop(key, None)
    
    def process_response(
        self,
        remote_jid: str,
        participant: Optional[str] = None,
        text: str = ""
    ) -> bool:
        """
        Processa resposta recebida
        
        Args:
            remote_jid: JID do contato
            participant: JID do participante (para grupos)
            text: Texto da resposta
        
        Returns:
            True se havia uma espera ativa para este contato
        """
        key = self._get_key(remote_jid, participant)
        
        if key in self._waiting_responses:
            future = self._waiting_responses[key]
            if not future.done():
                future.set_result(text)
            return True
        
        return False
    
    def cancel_wait(self, remote_jid: str, participant: Optional[str] = None):
        """Cancela espera ativa"""
        key = self._get_key(remote_jid, participant)
        if key in self._waiting_responses:
            future = self._waiting_responses.pop(key)
            if not future.done():
                future.cancel()


# Instância global
_wait_manager = WaitMessageManager()


def wait_response(remote_jid: str, participant: Optional[str] = None, timeout: int = 30000) -> str:
    """Função helper para esperar resposta"""
    return _wait_manager.wait_response(remote_jid, participant, timeout)


def process_response(remote_jid: str, participant: Optional[str] = None, text: str = "") -> bool:
    """Função helper para processar resposta"""
    return _wait_manager.process_response(remote_jid, participant, text)

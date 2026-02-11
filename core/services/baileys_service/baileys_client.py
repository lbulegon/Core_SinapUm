"""
Baileys Client - Cliente Principal
===================================

Cliente principal para conexão WhatsApp usando Baileys (Python).
Equivalente ao main.js e auth.js do projeto Node.js.

NOTA: Este é um esqueleto base. Para uso completo, você precisará:
1. Instalar uma biblioteca Python de WhatsApp Web (ex: whatsapp-web.py, yowsup)
2. Ou criar um wrapper para executar o projeto Node.js Baileys como subprocess
3. Ou usar uma API REST que exponha o Baileys Node.js

Por enquanto, esta implementação fornece a estrutura e interface.
"""
import asyncio
import logging
import json
import qrcode
import io
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from datetime import datetime

from .config import SESSIONS_DIR, MEDIA_DIR, RECONNECT_DELAY, MAX_RECONNECT_ATTEMPTS
from .exceptions import BaileysConnectionError, BaileysAuthError, BaileysMessageError, BaileysQRCodeError
from .utils.filter_logs import setup_log_filter
from .utils.wait_message import WaitMessageManager
from .utils.audit_events import audit_event, audit_connection_update, audit_disconnect

logger = logging.getLogger(__name__)


class BaileysClient:
    """
    Cliente Baileys para WhatsApp
    
    Gerencia conexão, autenticação, envio e recebimento de mensagens.
    """
    
    def __init__(self, session_name: str = "baileys-default"):
        """
        Inicializa cliente Baileys
        
        Args:
            session_name: Nome da sessão (usado para armazenar credenciais)
        """
        self.session_name = session_name
        self.session_dir = SESSIONS_DIR / session_name
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        self._connected = False
        self._reconnect_attempts = 0
        self._socket = None  # Será inicializado com biblioteca de WhatsApp
        self._wait_manager = WaitMessageManager()
        self._message_handlers: list[Callable] = []
        
        # Configura filtro de logs
        setup_log_filter()
    
    async def connect(self) -> bool:
        """
        Conecta ao WhatsApp
        
        Returns:
            True se conectado com sucesso
        
        Raises:
            BaileysConnectionError: Se conexão falhar
        """
        try:
            logger.info(f"Conectando ao WhatsApp (sessão: {self.session_name})...")
            
            # Carrega estado de autenticação
            auth_state = await self._load_auth_state()
            
            if not auth_state:
                # Precisa autenticar (gerar QR code)
                logger.info("Sessão não autenticada. Gerando QR code...")
                qr_code = await self._generate_qr_code()
                if qr_code:
                    self._display_qr_code(qr_code)
                    # Aguarda autenticação
                    await self._wait_for_auth()
            
            # Conecta socket
            await self._connect_socket(auth_state)
            
            self._connected = True
            self._reconnect_attempts = 0
            logger.info("✅ Conectado ao WhatsApp!")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar: {e}", exc_info=True)
            raise BaileysConnectionError(f"Erro ao conectar: {e}")
    
    async def disconnect(self):
        """Desconecta do WhatsApp"""
        if self._socket:
            try:
                await self._socket.disconnect()
            except Exception as e:
                logger.error(f"Erro ao desconectar: {e}")
            finally:
                self._socket = None
                self._connected = False
    
    async def send_text(self, to: str, text: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto
        
        Args:
            to: Número de destino (formato: 5511999999999)
            text: Texto da mensagem
        
        Returns:
            Dicionário com resultado (message_id, status, etc.)
        
        Raises:
            BaileysMessageError: Se envio falhar
        """
        if not self._connected:
            raise BaileysMessageError("Cliente não está conectado")
        
        try:
            # Formata número
            jid = self._format_jid(to)
            
            # Envia mensagem (implementação depende da biblioteca usada)
            result = await self._send_message(jid, {"text": text})
            
            logger.info(f"Mensagem enviada para {to}: {text[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}", exc_info=True)
            raise BaileysMessageError(f"Erro ao enviar mensagem: {e}")
    
    async def send_image(self, to: str, image_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia imagem
        
        Args:
            to: Número de destino
            image_path: Caminho da imagem
            caption: Legenda (opcional)
        
        Returns:
            Dicionário com resultado
        """
        if not self._connected:
            raise BaileysMessageError("Cliente não está conectado")
        
        try:
            jid = self._format_jid(to)
            image_data = Path(image_path).read_bytes()
            
            result = await self._send_media(jid, image_data, "image", caption)
            
            logger.info(f"Imagem enviada para {to}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao enviar imagem: {e}", exc_info=True)
            raise BaileysMessageError(f"Erro ao enviar imagem: {e}")
    
    async def send_document(self, to: str, document_path: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """
        Envia documento
        
        Args:
            to: Número de destino
            document_path: Caminho do documento
            caption: Legenda (opcional)
        
        Returns:
            Dicionário com resultado
        """
        if not self._connected:
            raise BaileysMessageError("Cliente não está conectado")
        
        try:
            jid = self._format_jid(to)
            document_data = Path(document_path).read_bytes()
            
            result = await self._send_media(jid, document_data, "document", caption)
            
            logger.info(f"Documento enviado para {to}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao enviar documento: {e}", exc_info=True)
            raise BaileysMessageError(f"Erro ao enviar documento: {e}")
    
    def on_message(self, handler: Callable):
        """
        Registra handler para mensagens recebidas
        
        Args:
            handler: Função async que recebe (from, text, message_data)
        """
        self._message_handlers.append(handler)
    
    async def wait_response(self, remote_jid: str, participant: Optional[str] = None, timeout: int = 30000) -> str:
        """
        Espera por resposta de um contato
        
        Args:
            remote_jid: JID do contato
            participant: JID do participante (para grupos)
            timeout: Timeout em milissegundos
        
        Returns:
            Texto da resposta
        """
        return await self._wait_manager.wait_response(remote_jid, participant, timeout)
    
    # Métodos privados
    
    async def _load_auth_state(self) -> Optional[Dict[str, Any]]:
        """Carrega estado de autenticação do disco"""
        creds_file = self.session_dir / "creds.json"
        keys_file = self.session_dir / "keys.json"
        
        if creds_file.exists() and keys_file.exists():
            try:
                creds = json.loads(creds_file.read_text())
                keys = json.loads(keys_file.read_text())
                return {"creds": creds, "keys": keys}
            except Exception as e:
                logger.warning(f"Erro ao carregar auth state: {e}")
        
        return None
    
    async def _save_auth_state(self, creds: Dict[str, Any], keys: Dict[str, Any]):
        """Salva estado de autenticação no disco"""
        creds_file = self.session_dir / "creds.json"
        keys_file = self.session_dir / "keys.json"
        
        creds_file.write_text(json.dumps(creds, indent=2))
        keys_file.write_text(json.dumps(keys, indent=2))
    
    async def _generate_qr_code(self) -> Optional[str]:
        """Gera QR code para autenticação"""
        # Implementação depende da biblioteca usada
        # Por enquanto, retorna None (será implementado com biblioteca real)
        raise NotImplementedError("QR code generation requires WhatsApp library")
    
    def _display_qr_code(self, qr_data: str):
        """Exibe QR code no terminal"""
        try:
            qr = qrcode.QRCode()
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Gera QR code ASCII
            f = io.StringIO()
            qr.print_ascii(out=f, invert=True)
            qr_str = f.getvalue()
            
            print("\n" + "="*50)
            print("ESCANEIE O QR CODE COM SEU WHATSAPP:")
            print("="*50)
            print(qr_str)
            print("="*50 + "\n")
            
        except Exception as e:
            logger.error(f"Erro ao exibir QR code: {e}")
            raise BaileysQRCodeError(f"Erro ao exibir QR code: {e}")
    
    async def _wait_for_auth(self):
        """Aguarda autenticação via QR code"""
        # Implementação depende da biblioteca usada
        # Aguarda até que credenciais sejam salvas
        max_wait = 300  # 5 minutos
        waited = 0
        
        while waited < max_wait:
            await asyncio.sleep(2)
            auth_state = await self._load_auth_state()
            if auth_state:
                return
            waited += 2
        
        raise BaileysAuthError("Timeout aguardando autenticação")
    
    async def _connect_socket(self, auth_state: Optional[Dict[str, Any]]):
        """Conecta socket WhatsApp"""
        # Implementação depende da biblioteca usada
        # Por enquanto, apenas marca como conectado
        # Em implementação real, aqui seria a conexão com a biblioteca de WhatsApp
        self._socket = {"connected": True}  # Placeholder
    
    async def _send_message(self, jid: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Envia mensagem via socket"""
        # Implementação depende da biblioteca usada
        # Placeholder
        return {"message_id": f"msg_{datetime.now().timestamp()}", "status": "sent"}
    
    async def _send_media(self, jid: str, media_data: bytes, media_type: str, caption: Optional[str] = None) -> Dict[str, Any]:
        """Envia mídia via socket"""
        # Implementação depende da biblioteca usada
        # Placeholder
        return {"message_id": f"media_{datetime.now().timestamp()}", "status": "sent"}
    
    def _format_jid(self, number: str) -> str:
        """Formata número para JID"""
        # Remove caracteres não numéricos
        number = ''.join(filter(str.isdigit, number))
        return f"{number}@s.whatsapp.net"
    
    def _handle_message(self, message_data: Dict[str, Any]):
        """Processa mensagem recebida"""
        from_jid = message_data.get('from')
        text = message_data.get('text', '')
        participant = message_data.get('participant')
        
        # Processa resposta esperada
        self._wait_manager.process_response(from_jid, participant, text)
        
        # Chama handlers registrados
        for handler in self._message_handlers:
            try:
                asyncio.create_task(handler(from_jid, text, message_data))
            except Exception as e:
                logger.error(f"Erro no handler de mensagem: {e}")
    
    @property
    def is_connected(self) -> bool:
        """Verifica se está conectado"""
        return self._connected

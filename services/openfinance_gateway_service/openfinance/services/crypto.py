"""
Criptografia AES-GCM para tokens Open Finance.
Formato: v1:<base64(nonce+ciphertext+tag)>
"""
import base64
import os
from typing import Optional

from django.conf import settings
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def _get_key() -> bytes:
    """Obtém chave de 32 bytes do ambiente."""
    key_str = getattr(settings, 'OPENFINANCE_TOKEN_KEY', '') or os.environ.get('OPENFINANCE_TOKEN_KEY', '')
    if not key_str or len(key_str.encode('utf-8')) < 32:
        raise ValueError(
            "OPENFINANCE_TOKEN_KEY ausente ou muito curta. "
            "Defina variável de ambiente com pelo menos 32 caracteres."
        )
    key_bytes = key_str.encode('utf-8')[:32]
    if len(key_bytes) < 32:
        key_bytes = key_bytes.ljust(32, b'\0')
    return key_bytes


def encrypt_text(plain: str) -> str:
    """
    Criptografa texto com AES-GCM.
    Retorna formato v1:<base64(nonce+ciphertext+tag)>.
    """
    key = _get_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    plain_bytes = plain.encode('utf-8')
    ciphertext = aesgcm.encrypt(nonce, plain_bytes, None)
    payload = nonce + ciphertext
    b64 = base64.b64encode(payload).decode('ascii')
    return f"v1:{b64}"


def decrypt_text(enc: str) -> str:
    """
    Descriptografa payload no formato v1:<base64(nonce+ciphertext+tag)>.
    """
    if not enc or not enc.startswith('v1:'):
        raise ValueError("Formato de payload inválido. Esperado v1:<base64>")
    key = _get_key()
    b64 = enc[3:]
    payload = base64.b64decode(b64)
    if len(payload) < 12 + 16:  # nonce(12) + tag(16)
        raise ValueError("Payload criptografado inválido ou truncado")
    nonce = payload[:12]
    ciphertext = payload[12:]
    aesgcm = AESGCM(key)
    plain_bytes = aesgcm.decrypt(nonce, ciphertext, None)
    return plain_bytes.decode('utf-8')

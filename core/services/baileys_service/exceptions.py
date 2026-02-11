"""
Exceções do Baileys Service
============================
"""


class BaileysError(Exception):
    """Exceção base para erros do Baileys Service"""
    pass


class BaileysConnectionError(BaileysError):
    """Erro de conexão com WhatsApp"""
    pass


class BaileysAuthError(BaileysError):
    """Erro de autenticação"""
    pass


class BaileysMessageError(BaileysError):
    """Erro ao enviar/receber mensagem"""
    pass


class BaileysQRCodeError(BaileysError):
    """Erro ao gerar QR Code"""
    pass

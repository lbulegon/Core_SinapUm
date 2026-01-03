"""
Utilitários para validação HMAC e segurança do Lead Registry.
"""
import hmac
import hashlib
import time
from django.core.cache import cache
from django.conf import settings


def generate_hmac_signature(secret: str, project_key: str, timestamp: str, email: str, whatsapp: str) -> str:
    """
    Gera assinatura HMAC-SHA256 para validação de requisições.
    
    Args:
        secret: Secret do projeto (ProjectCredential.project_secret)
        project_key: Identificador do projeto
        timestamp: Timestamp Unix (string)
        email: Email do lead
        whatsapp: WhatsApp do lead
    
    Returns:
        Assinatura hexadecimal HMAC-SHA256
    """
    # Mensagem a ser assinada: project_key + timestamp + email + whatsapp
    message = f"{project_key}{timestamp}{email}{whatsapp}"
    
    # Gerar HMAC-SHA256
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def validate_hmac_signature(
    project_key: str,
    signature: str,
    timestamp: str,
    email: str,
    whatsapp: str,
    window_seconds: int = 300  # 5 minutos
) -> tuple[bool, str]:
    """
    Valida assinatura HMAC e timestamp.
    
    Args:
        project_key: Identificador do projeto
        signature: Assinatura recebida
        timestamp: Timestamp Unix recebido
        email: Email do lead
        whatsapp: WhatsApp do lead
        window_seconds: Janela de tempo válida em segundos (padrão: 5 minutos)
    
    Returns:
        Tupla (is_valid, error_message)
    """
    import logging
    logger = logging.getLogger(__name__)
    
    from .models import ProjectCredential
    
    # Buscar credencial do projeto
    try:
        credential = ProjectCredential.objects.get(project_key=project_key, is_active=True)
    except ProjectCredential.DoesNotExist:
        logger.error(f"❌ ProjectCredential não encontrado ou inativo: {project_key}")
        return False, "Projeto não autorizado ou inativo"
    
    # Validar timestamp (evitar replay attacks)
    try:
        timestamp_int = int(timestamp)
        current_time = int(time.time())
        time_diff = abs(current_time - timestamp_int)
        
        if time_diff > window_seconds:
            logger.warning(
                f"❌ Timestamp fora da janela: diff={time_diff}s | "
                f"received={timestamp_int} | current={current_time}"
            )
            return False, f"Timestamp fora da janela válida (diferença: {time_diff}s)"
    except (ValueError, TypeError) as e:
        logger.error(f"❌ Timestamp inválido: {timestamp} | Erro: {e}")
        return False, "Timestamp inválido"
    
    # Gerar assinatura esperada
    expected_signature = generate_hmac_signature(
        credential.project_secret,
        project_key,
        timestamp,
        email,
        whatsapp
    )
    
    # Log detalhado para debug (apenas em caso de falha)
    if not hmac.compare_digest(signature, expected_signature):
        message = f"{project_key}{timestamp}{email}{whatsapp}"
        logger.error(
            f"❌ HMAC signature mismatch:\n"
            f"   Received: {signature}\n"
            f"   Expected: {expected_signature}\n"
            f"   Message: {message}\n"
            f"   Project Key: {project_key}\n"
            f"   Secret (first 20): {credential.project_secret[:20]}..."
        )
        return False, "Assinatura HMAC inválida"
    
    return True, ""


def get_client_ip(request) -> str:
    """
    Extrai o IP real do cliente, considerando proxies.
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        # X-Forwarded-For pode conter múltiplos IPs (proxy chain)
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def rate_limit_check(request, key_prefix: str = "lead_capture", limit: int = 20, window_seconds: int = 60) -> bool:
    """
    Verifica rate limit por IP usando cache.
    
    Args:
        request: HttpRequest do Django
        key_prefix: Prefixo da chave de cache
        limit: Limite de requisições
        window_seconds: Janela de tempo em segundos
    
    Returns:
        True se dentro do limite, False se excedido
    """
    ip = get_client_ip(request) or "unknown"
    cache_key = f"{key_prefix}:{ip}"
    
    current = cache.get(cache_key, 0)
    if current >= limit:
        return False
    
    # Incrementar contador
    cache.set(cache_key, current + 1, window_seconds)
    return True


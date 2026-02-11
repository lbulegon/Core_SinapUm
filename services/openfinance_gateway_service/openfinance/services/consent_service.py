"""
Serviço de consentimento Open Finance.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from django.utils import timezone

from ..models import OF_Consent, OF_Credential, OF_AuditLog
from .crypto import encrypt_text
from .provider_stub import create_consent, exchange_token


def _audit(consent: Optional[OF_Consent], user_id: str, origin_system: str, action: str, meta: dict = None):
    """Registra ação no audit log."""
    OF_AuditLog.objects.create(
        consent=consent,
        user_id=user_id,
        origin_system=origin_system,
        action=action,
        meta=meta or {},
    )


def create_consent_for_user(user_id: str, origin_system: str, scope: dict) -> OF_Consent:
    """
    Cria novo consentimento e retorna o objeto OF_Consent com redirect_url.
    """
    provider_result = create_consent(user_id, scope)
    consent = OF_Consent.objects.create(
        user_id=user_id,
        origin_system=origin_system,
        provider='stub',
        status='PENDING',
        scope=scope,
        external_consent_id=provider_result['external_consent_id'],
        expires_at=provider_result['expires_at'],
    )
    consent._redirect_url = provider_result['redirect_url']
    _audit(consent, user_id, origin_system, 'consent_create', {'consent_id': str(consent.id)})
    return consent


def approve_consent_from_callback(consent_id: str, callback_params: dict) -> OF_Consent:
    """
    Aprova consentimento via callback do provider.
    Troca tokens e cria OF_Credential criptografado.
    """
    consent = OF_Consent.objects.get(id=consent_id)
    if consent.status != 'PENDING':
        raise ValueError(f"Consent {consent_id} não está PENDING (status={consent.status})")

    provider_result = exchange_token(consent.external_consent_id, callback_params)
    access_enc = encrypt_text(provider_result['access_token'])
    refresh_enc = encrypt_text(provider_result['refresh_token'])

    OF_Credential.objects.create(
        consent=consent,
        access_token_enc=access_enc,
        refresh_token_enc=refresh_enc,
        token_expires_at=provider_result['token_expires_at'],
        key_version=1,
    )
    consent.status = 'APPROVED'
    consent.approved_at = timezone.now()
    consent.save(update_fields=['status', 'approved_at'])

    _audit(consent, consent.user_id, consent.origin_system, 'consent_approved', {'consent_id': str(consent.id)})
    return consent

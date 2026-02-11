"""
Provider stub para Open Finance - retorna dados simulados coerentes.
Interface para implementação real futura.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional


def create_consent(user_id: str, scope: dict) -> Dict[str, Any]:
    """
    Cria consentimento no provider (stub).
    Returns: {external_consent_id, redirect_url, expires_at}
    """
    external_id = f"stub-{user_id[:8]}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    expires_at = datetime.utcnow() + timedelta(hours=24)
    return {
        'external_consent_id': external_id,
        'redirect_url': f"https://stub-provider.example/callback?consent_id={external_id}",
        'expires_at': expires_at,
    }


def exchange_token(external_consent_id: str, callback_params: dict) -> Dict[str, Any]:
    """
    Troca código/callback por tokens (stub).
    Returns: {access_token, refresh_token, token_expires_at}
    """
    token_expires_at = datetime.utcnow() + timedelta(hours=1)
    return {
        'access_token': f"stub-at-{external_consent_id}",
        'refresh_token': f"stub-rt-{external_consent_id}",
        'token_expires_at': token_expires_at,
    }


def fetch_accounts(access_token: str) -> List[Dict[str, Any]]:
    """
    Busca contas do usuário (stub).
    """
    return [
        {
            'external_account_id': 'stub-acc-001',
            'type': 'checking',
            'currency': 'BRL',
            'masked_number': '****1234',
            'owner_name': 'Usuario Teste',
            'owner_doc': '***.***.***-**',
        },
        {
            'external_account_id': 'stub-acc-002',
            'type': 'savings',
            'currency': 'BRL',
            'masked_number': '****5678',
            'owner_name': 'Usuario Teste',
            'owner_doc': '***.***.***-**',
        },
    ]


def fetch_transactions(
    access_token: str,
    external_account_id: str,
    from_date: datetime,
    to_date: datetime,
) -> List[Dict[str, Any]]:
    """
    Busca transações da conta (stub).
    """
    txs = []
    for i in range(1, 6):
        direction = 'IN' if i % 2 == 0 else 'OUT'
        amount = Decimal(str(100.00 * i))
        if direction == 'OUT':
            amount = -amount
        txs.append({
            'external_tx_id': f"stub-tx-{external_account_id[-3:]}-{i:04d}",
            'date': (from_date + timedelta(days=i)).isoformat(),
            'amount': str(amount),
            'direction': direction,
            'description': f'Transacao stub {i}',
            'description_hash': f"hash-{i}",
        })
    return txs

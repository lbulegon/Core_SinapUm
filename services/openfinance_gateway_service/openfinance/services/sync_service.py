"""
Serviço de sincronização de contas e transações.
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Tuple

from django.utils import timezone

from ..models import OF_Consent, OF_Credential, OF_Account, OF_Transaction, OF_DataSnapshot, OF_AuditLog
from .crypto import decrypt_text
from .provider_stub import fetch_accounts, fetch_transactions


def _get_access_token(consent: OF_Consent) -> str:
    """Obtém access token descriptografado."""
    cred = consent.credential
    if not cred:
        raise ValueError("Consent não possui credencial")
    return decrypt_text(cred.access_token_enc)


def _audit(consent: OF_Consent, action: str, meta: dict = None):
    OF_AuditLog.objects.create(
        consent=consent,
        user_id=consent.user_id,
        origin_system=consent.origin_system,
        action=action,
        meta=meta or {},
    )


def sync_accounts(consent: OF_Consent) -> List[OF_Account]:
    """Sincroniza contas do consentimento."""
    access_token = _get_access_token(consent)
    accounts_data = fetch_accounts(access_token)
    created_accounts = []
    for acc_data in accounts_data:
        acc, created = OF_Account.objects.update_or_create(
            consent=consent,
            external_account_id=acc_data['external_account_id'],
            defaults={
                'type': acc_data.get('type', 'checking'),
                'currency': acc_data.get('currency', 'BRL'),
                'masked_number': acc_data.get('masked_number', ''),
                'owner_name': acc_data.get('owner_name'),
                'owner_doc': acc_data.get('owner_doc'),
            },
        )
        if created:
            created_accounts.append(acc)

    OF_DataSnapshot.objects.create(
        consent=consent,
        snapshot_type='ACCOUNTS',
        payload={'accounts': [a.external_account_id for a in consent.accounts.all()]},
    )
    _audit(consent, 'sync_accounts', {'count': len(accounts_data)})
    return list(consent.accounts.all())


def sync_transactions(
    consent: OF_Consent,
    from_date: datetime = None,
    to_date: datetime = None,
) -> Tuple[List[OF_Account], List[OF_Transaction]]:
    """
    Sincroniza contas e transações.
    Retorna (accounts, transactions).
    """
    if not from_date:
        from_date = timezone.now() - timedelta(days=30)
    if not to_date:
        to_date = timezone.now()

    accounts = sync_accounts(consent)
    access_token = _get_access_token(consent)
    all_txs = []
    for acc in accounts:
        txs_data = fetch_transactions(
            access_token,
            acc.external_account_id,
            from_date,
            to_date,
        )
        for tx_data in txs_data:
            tx_date = tx_data.get('date')
            if isinstance(tx_date, str):
                tx_date = datetime.fromisoformat(tx_date.replace('Z', '+00:00'))
            if tx_date and getattr(tx_date, 'tzinfo', None) is None:
                tx_date = timezone.make_aware(tx_date) if timezone.is_naive(tx_date) else tx_date
            tx, _ = OF_Transaction.objects.update_or_create(
                account=acc,
                external_tx_id=tx_data['external_tx_id'],
                defaults={
                    'date': tx_date,
                    'amount': Decimal(str(tx_data['amount']).replace('-', '')),
                    'direction': tx_data['direction'],
                    'description': tx_data.get('description', ''),
                    'description_hash': tx_data.get('description_hash', ''),
                },
            )
            all_txs.append(tx)

    OF_DataSnapshot.objects.create(
        consent=consent,
        snapshot_type='TRANSACTIONS',
        payload={'count': len(all_txs)},
    )
    _audit(consent, 'sync_transactions', {'count': len(all_txs)})
    return accounts, all_txs

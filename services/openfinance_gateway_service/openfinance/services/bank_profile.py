"""
Perfil bancário resumido para scoring/risco.
"""
from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count
from django.db.models.functions import Coalesce

from ..models import OF_Consent, OF_Account, OF_Transaction


def build_bank_profile(consent: OF_Consent) -> dict:
    """
    Constrói resumo do perfil bancário.
    Retorna: {qtd_contas, volume_30d_in, volume_30d_out, recorrencia_entradas, flags}
    """
    cutoff = timezone.now() - timedelta(days=30)
    accounts = consent.accounts.all()
    qtd_contas = accounts.count()

    volume_in = Decimal('0')
    volume_out = Decimal('0')
    tx_dates_in = []

    for acc in accounts:
        txs_in = acc.transactions.filter(direction='IN', date__gte=cutoff)
        txs_out = acc.transactions.filter(direction='OUT', date__gte=cutoff)
        vol_in = txs_in.aggregate(s=Coalesce(Sum('amount'), Decimal('0')))['s']
        vol_out = txs_out.aggregate(s=Coalesce(Sum('amount'), Decimal('0')))['s']
        volume_in += vol_in
        volume_out += vol_out
        for t in txs_in:
            tx_dates_in.append(t.date.date())

    # Heurística simples de recorrência: entradas em pelo menos 2 dias distintos no mês
    tx_dates_unique = sorted(set(tx_dates_in))
    recorrencia_entradas = len(tx_dates_unique) >= 2

    flags = []
    if qtd_contas == 0:
        flags.append('sem_dados')
    if volume_in == 0 and volume_out == 0 and qtd_contas > 0:
        flags.append('sem_transacoes_30d')
    if len(accounts) > 5:
        flags.append('muitas_contas')

    return {
        'qtd_contas': qtd_contas,
        'volume_30d_in': float(volume_in),
        'volume_30d_out': float(volume_out),
        'recorrencia_entradas': recorrencia_entradas,
        'flags': flags,
    }

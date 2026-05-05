"""
Parsing e verificação de assinatura dos webhooks Stripe (execução).
O despacho por tipo de evento permanece em ``app_platform_billing.stripe_dispatch``.
"""

from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse


def parse_stripe_webhook_event(
    payload: bytes, sig_header: str
) -> tuple[dict | None, HttpResponse | None]:
    """
    Constrói o evento Stripe verificando a assinatura.
    Retorna ``(event, None)`` em sucesso ou ``(None, response_erro)``.
    """
    if not getattr(settings, "STRIPE_WEBHOOK_SECRET", None):
        return None, HttpResponse("Webhook não configurado", status=503)

    try:
        import stripe
    except ImportError:
        return None, HttpResponse("stripe não instalado", status=503)

    stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "") or ""

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return None, HttpResponse("payload inválido", status=400)
    except Exception as e:
        if "Signature" in type(e).__name__:
            return None, HttpResponse("assinatura inválida", status=400)
        raise

    return event, None

"""Utilitários Stripe partilhados (webhook + checkout)."""

from __future__ import annotations


def stripe_obj_get(obj: object, key: str):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def stripe_subscription_price_id(sub: object) -> str | None:
    try:
        items = stripe_obj_get(sub, "items")
        if isinstance(items, dict):
            data = items.get("data") or []
        else:
            data = getattr(items, "data", None) or []
        if not data:
            return None
        first = data[0]
        if isinstance(first, dict):
            price = first.get("price")
        else:
            price = getattr(first, "price", None)
        if isinstance(price, str):
            return price
        if isinstance(price, dict):
            return price.get("id")
        return getattr(price, "id", None) if price is not None else None
    except Exception:
        return None


def stripe_period_end_aware(sub: object):
    from datetime import datetime, timezone as py_tz

    from django.utils import timezone as dj_tz

    ts = stripe_obj_get(sub, "current_period_end")
    if not ts:
        return None
    try:
        period_end = datetime.fromtimestamp(int(ts), tz=py_tz.utc)
        if dj_tz.is_naive(period_end):
            period_end = dj_tz.make_aware(period_end)
        return period_end
    except Exception:
        return None

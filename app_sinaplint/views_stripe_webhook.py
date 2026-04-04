"""
Webhook Stripe (assinatura criada / atualizada).
"""

from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View


def _stripe_obj_get(obj: object, key: str):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def _stripe_subscription_price_id(sub: object) -> str | None:
    try:
        items = _stripe_obj_get(sub, "items")
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


def _stripe_period_end(sub: object):
    from datetime import datetime, timezone as py_tz

    from django.utils import timezone as dj_tz

    ts = _stripe_obj_get(sub, "current_period_end")
    if not ts:
        return None
    try:
        period_end = datetime.fromtimestamp(int(ts), tz=py_tz.utc)
        if dj_tz.is_naive(period_end):
            period_end = dj_tz.make_aware(period_end)
        return period_end
    except Exception:
        return None


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """POST bruto — verificação de assinatura Stripe."""

    def post(self, request, *args, **kwargs):
        if not getattr(settings, "STRIPE_WEBHOOK_SECRET", None):
            return HttpResponse("Webhook não configurado", status=503)

        try:
            import stripe
        except ImportError:
            return HttpResponse("stripe não instalado", status=503)

        stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")

        payload = request.body
        sig = request.META.get("HTTP_STRIPE_SIGNATURE", "")

        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            return HttpResponse("payload inválido", status=400)
        except Exception as e:
            if "Signature" in type(e).__name__:
                return HttpResponse("assinatura inválida", status=400)
            raise

        if event["type"] == "checkout.session.completed":
            self._handle_checkout_completed(event["data"]["object"])

        if event["type"] == "customer.subscription.updated":
            self._handle_subscription_updated(event["data"]["object"])

        if event["type"] == "customer.subscription.deleted":
            self._handle_subscription_deleted(event["data"]["object"])

        return HttpResponse(status=200)

    def _handle_checkout_completed(self, session: dict) -> None:
        from django.contrib.auth import get_user_model

        from app_sinaplint.models_billing import Plan, Subscription

        User = get_user_model()
        meta = session.get("metadata") or {}
        uid = meta.get("user_id")
        if not uid:
            return
        try:
            user = User.objects.get(pk=int(uid))
        except (User.DoesNotExist, ValueError, TypeError):
            return

        sub_id = session.get("subscription")
        customer_id = session.get("customer")
        if not sub_id or not customer_id:
            return

        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY
        sub = stripe.Subscription.retrieve(sub_id, expand=["items.data.price"])
        price_id = _stripe_subscription_price_id(sub)

        plan = None
        if price_id:
            plan = Plan.objects.filter(stripe_price_id=price_id).first()

        period_end = _stripe_period_end(sub)

        status_s = _stripe_obj_get(sub, "status") or "active"
        Subscription.objects.update_or_create(
            user=user,
            defaults={
                "stripe_customer_id": customer_id,
                "stripe_subscription_id": sub_id,
                "plan": plan,
                "status": str(status_s),
                "current_period_end": period_end,
            },
        )

    def _handle_subscription_updated(self, sub_obj: dict) -> None:
        from django.contrib.auth import get_user_model

        from app_sinaplint.models_billing import Plan, Subscription

        meta = sub_obj.get("metadata") or {}
        uid = meta.get("user_id")
        customer_id = sub_obj.get("customer")
        sub_id = sub_obj.get("id")
        status_s = sub_obj.get("status")

        User = get_user_model()
        user = None
        if uid:
            try:
                user = User.objects.get(pk=int(uid))
            except (User.DoesNotExist, ValueError, TypeError):
                pass
        if not user and customer_id:
            user = (
                Subscription.objects.filter(stripe_customer_id=customer_id)
                .values_list("user_id", flat=True)
                .first()
            )
            if user:
                user = User.objects.filter(pk=user).first()

        if not user:
            return

        price_id = _stripe_subscription_price_id(sub_obj)

        plan = Plan.objects.filter(stripe_price_id=price_id).first() if price_id else None

        period_end = _stripe_period_end(sub_obj)

        Subscription.objects.update_or_create(
            user=user,
            defaults={
                "stripe_subscription_id": sub_id or "",
                "stripe_customer_id": customer_id or "",
                "plan": plan,
                "status": str(status_s) if status_s else "active",
                "current_period_end": period_end,
            },
        )

    def _handle_subscription_deleted(self, sub_obj: dict) -> None:
        from app_sinaplint.models_billing import Subscription

        customer_id = sub_obj.get("customer")
        if not customer_id:
            return
        Subscription.objects.filter(stripe_customer_id=customer_id).update(
            status="canceled",
            stripe_subscription_id="",
        )

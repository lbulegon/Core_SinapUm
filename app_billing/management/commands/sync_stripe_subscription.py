"""Sincroniza uma Subscription Stripe com ``PlatformSubscription`` (manual / drift)."""

from __future__ import annotations

from django.core.management.base import BaseCommand

from app_billing.services.sync_service import sync_subscription


class Command(BaseCommand):
    help = (
        "Busca uma Subscription na Stripe (sub_...) e atualiza o PlatformSubscription local. "
        "Útil após falha de webhook ou inconsistência."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "subscription_id",
            type=str,
            help="ID da subscription na Stripe (ex.: sub_xxx).",
        )

    def handle(self, *args, **options):
        sid = options["subscription_id"].strip()
        result = sync_subscription(sid)
        if result.ok and result.platform_subscription:
            ps = result.platform_subscription
            self.stdout.write(self.style.SUCCESS(result.message))
            self.stdout.write(
                f"  PlatformSubscription id={ps.pk} user={ps.user_id} "
                f"product={ps.product.slug} status={ps.status}"
            )
        else:
            self.stdout.write(self.style.ERROR(result.message))

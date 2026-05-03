"""
Cria ou atualiza planos Free / Pro / Scale no catálogo plataforma (produto ``sinaplint``).

    python manage.py sinaplint_seed_plans
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from app_platform_billing.default_catalog import upsert_sinaplint_catalog_plans


class Command(BaseCommand):
    help = "Semeia planos SinapLint no catálogo plataforma (substitui stripe_price_id pelos reais no Stripe)."

    def handle(self, *args, **options):
        total, created = upsert_sinaplint_catalog_plans()
        self.stdout.write(self.style.SUCCESS(f"Planos sinaplint no catálogo: {total} (novos: {created})."))
        self.stdout.write(
            self.style.WARNING(
                "Defina stripe_price_id em Admin (app_platform_billing) para Pro/Scale; checkout sem price falha."
            )
        )

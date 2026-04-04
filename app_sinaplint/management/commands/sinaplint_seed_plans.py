"""
Cria ou atualiza planos Free / Pro / Scale (preços Stripe = placeholders).

    python manage.py sinaplint_seed_plans
"""

from __future__ import annotations

from django.core.management.base import BaseCommand

from app_sinaplint.models_billing import Plan


class Command(BaseCommand):
    help = "Semeia planos SinapLint SaaS (substitui price_id pelos reais no Stripe Dashboard)."

    def handle(self, *args, **options):
        defaults = [
            {
                "name": "Free",
                "slug": "free",
                "stripe_price_id": "",
                "max_analyses_per_month": 10,
                "max_repos": 5,
                "sort_order": 0,
            },
            {
                "name": "Pro",
                "slug": "pro",
                "stripe_price_id": "",
                "max_analyses_per_month": 200,
                "max_repos": 25,
                "sort_order": 10,
            },
            {
                "name": "Scale",
                "slug": "scale",
                "stripe_price_id": "",
                "max_analyses_per_month": -1,
                "max_repos": 500,
                "sort_order": 20,
            },
        ]
        for row in defaults:
            slug = row.pop("slug")
            Plan.objects.update_or_create(slug=slug, defaults=row)
            self.stdout.write(self.style.SUCCESS(f"Plan {slug} OK"))

        self.stdout.write(
            self.style.WARNING(
                "Defina stripe_price_id em Admin ou Stripe para Pro/Scale; checkout sem price falha."
            )
        )

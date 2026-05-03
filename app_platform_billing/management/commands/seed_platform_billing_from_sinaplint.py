"""
Garante produto ``sinaplint`` e planos por omissão no catálogo plataforma.

    python manage.py seed_platform_billing_from_sinaplint

(As tabelas legadas ``Plan`` / ``Subscription`` foram removidas; este comando
equivale a ``sinaplint_seed_plans``.)
"""

from django.core.management.base import BaseCommand

from app_platform_billing.default_catalog import upsert_sinaplint_catalog_plans


class Command(BaseCommand):
    help = "Semeia catálogo plataforma para SinapLint (idempotente)."

    def handle(self, *args, **options):
        total, created = upsert_sinaplint_catalog_plans()
        self.stdout.write(
            self.style.SUCCESS(
                f"Catálogo sinaplint: {total} plano(s); criados nesta execução: {created}."
            )
        )

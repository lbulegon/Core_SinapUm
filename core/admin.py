"""
Admin: auditoria de precificação.

O modelo :class:`~app_sinapcore.models.pricing_log.PricingLog` vive em ``app_sinapcore``;
este módulo é importado em :meth:`app_sinapcore.apps.AppSinapcoreConfig.ready` para registo
no site admin (o pacote ``core`` não é um INSTALLED_APPS).
"""
from __future__ import annotations

from django.contrib import admin

from app_sinapcore.models.pricing_log import PricingLog


@admin.register(PricingLog)
class PricingLogAdmin(admin.ModelAdmin):
    list_display = (
        "empresa_id",
        "produto_id",
        "preco_base",
        "preco_final",
        "fator_total",
        "multiplicador_verificacao",
        "canal",
        "timestamp",
    )
    list_filter = ("canal", "timestamp")
    search_fields = ("produto_id", "empresa_id", "motivo")
    ordering = ("-timestamp",)
    date_hierarchy = "timestamp"
    readonly_fields = (
        "empresa_id",
        "produto_id",
        "preco_base",
        "preco_final",
        "fator_total",
        "fatores",
        "fatores_formatados",
        "canal",
        "motivo",
        "timestamp",
    )

    @admin.display(description="Multiplicador (final/base)")
    def multiplicador_verificacao(self, obj: PricingLog) -> str:
        base = float(obj.preco_base)
        if base == 0:
            return "—"
        return str(round(float(obj.preco_final) / base, 4))

    @admin.display(description="Fatores (JSON)")
    def fatores_formatados(self, obj: PricingLog) -> str:
        fatores = obj.fatores or {}
        if not isinstance(fatores, dict):
            return str(fatores)
        return "\n".join(f"{k}: {v}" for k, v in fatores.items())

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

"""Rotas REST auxiliares do app_sinapcore (SinapLint Cloud)."""

from django.urls import path

from app_sinapcore import api_sinaplint_cloud, api_sinaplint_engine

urlpatterns = [
    path("v1/analyze/", api_sinaplint_cloud.analyze, name="sinaplint_cloud_analyze"),
    # Motor completo (JSON) — produto SinapLint SaaS (proxy HTTP)
    path(
        "internal/engine/",
        api_sinaplint_engine.engine_run,
        name="sinaplint_engine_run",
    ),
]

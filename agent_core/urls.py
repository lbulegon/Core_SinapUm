"""URLs do Agent Core (PAOR + integração com Architecture Intelligence)."""

from django.urls import path

from agent_core import views
from agent_core import views_dashboard

app_name = "agent_core"

urlpatterns = [
    path("health/", views.health, name="health"),
    path("dashboard/", views_dashboard.dashboard, name="dashboard"),
    # Demonstração PAOR — vários caminhos para compatibilidade com deploys antigos
    path("run-demo/", views_dashboard.run_demo_cycle, name="run_demo"),
    path("dashboard/run-demo/", views_dashboard.run_demo_cycle),
    path("run-with-governance/", views.run_with_governance, name="run_with_governance"),
    # Alias (alguns ambientes esperam governança sob dashboard)
    path("dashboard/governance/", views.run_with_governance),
]

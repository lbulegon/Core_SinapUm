from django.urls import path

from app_sinapcore import views

urlpatterns = [
    path("", views.sinapcore_dashboard, name="sinapcore_dashboard"),
    path("toggle/<int:module_id>/", views.toggle_module, name="toggle_module"),
    path("logs/<str:module_name>/", views.module_logs, name="module_logs"),
]

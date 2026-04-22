from django.urls import path

from app_sinapcore import api_agno

urlpatterns = [
    path("fila/", api_agno.agno_fila, name="agno_fila"),
    path("menu/", api_agno.agno_menu, name="agno_menu"),
    path("batch/", api_agno.agno_batch, name="agno_batch"),
    path("pricing/", api_agno.agno_pricing, name="agno_pricing"),
    path("chef/message/", api_agno.agno_chef_message, name="agno_chef_message"),
    path("flags/", api_agno.agno_flags, name="agno_flags"),
]

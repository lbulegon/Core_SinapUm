# ============================================================================
# ARQUITETURA NOVA - app_ai_bridge.urls
# ============================================================================

from django.urls import path
from . import views

app_name = 'app_ai_bridge'

urlpatterns = [
    path('inbound', views.inbound, name='inbound'),
    path('outbound', views.outbound, name='outbound'),
]


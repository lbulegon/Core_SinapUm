# ============================================================================
# ARQUITETURA NOVA - app_mcp.urls
# ============================================================================

from django.urls import path
from . import views

app_name = 'app_mcp'

urlpatterns = [
    path('tools/<str:tool_name>', views.execute_tool, name='execute_tool'),
]


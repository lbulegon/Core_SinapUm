"""
URLs do MCP Tool Registry
"""
from django.urls import path
from . import views

app_name = 'mcp_tool_registry'

urlpatterns = [
    path('tools/', views.list_tools, name='list_tools'),
    path('tools/<path:tool_name>/', views.get_tool_detail, name='get_tool_detail'),
    path('tools/resolve/', views.resolve_tool, name='resolve_tool'),
    path('tools/log/', views.log_tool_call, name='log_tool_call'),
]


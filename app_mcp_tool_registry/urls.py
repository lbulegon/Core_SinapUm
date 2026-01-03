"""
URLs do MCP Tool Registry
"""
from django.urls import path
from . import views

app_name = 'mcp_tool_registry'

urlpatterns = [
    path('tools/', views.list_tools, name='list_tools'),
    path('tools/<path:tool_name>/', views.get_tool_detail, name='get_tool_detail'),
    path('tools/<path:tool_name>/execute/', views.execute_tool_view, name='execute_tool'),
    path('tools/resolve/', views.resolve_tool, name='resolve_tool'),
    path('tools/log/', views.log_tool_call, name='log_tool_call'),
    path('executions/', views.list_executions, name='list_executions'),
]


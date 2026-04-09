from django.contrib import admin
from .models import AgentTask


@admin.register(AgentTask)
class AgentTaskAdmin(admin.ModelAdmin):
    list_display = ["task_id", "agent_name", "status", "created_at", "updated_at"]
    list_filter = ["status", "agent_name"]
    search_fields = ["task_id", "agent_name", "trace_id", "idempotency_key"]
    readonly_fields = ["task_id", "created_at", "updated_at", "started_at", "finished_at"]

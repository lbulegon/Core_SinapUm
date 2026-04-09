"""
Seed idempotente: Tools MCP mrfoo.graph.* (Food Knowledge Graph).
Cria Tool + ToolVersion com runtime mrfoo_graph e action no config.
"""
from django.core.management.base import BaseCommand
from app_mcp_tool_registry.models import ClientApp, Tool, ToolVersion


MRFOO_GRAPH_TOOLS = [
    ("mrfoo.graph.status", "Status do grafo FKG + health Neo4j", "status", {"type": "object", "properties": {"tenant_id": {"type": "string"}}, "required": ["tenant_id"]}),
    ("mrfoo.graph.sync_full", "Sync completo Postgres → Neo4j", "sync_full", {"type": "object", "properties": {"tenant_id": {"type": "string"}}, "required": ["tenant_id"]}),
    ("mrfoo.graph.sync_incremental", "Sync incremental", "sync_incremental", {"type": "object", "properties": {"tenant_id": {"type": "string"}}, "required": ["tenant_id"]}),
    ("mrfoo.graph.margin_per_minute", "Margem por minuto (timeslot)", "margin_per_minute", {"type": "object", "properties": {"tenant_id": {"type": "string"}, "timeslot": {"type": "string"}}, "required": ["tenant_id"]}),
    ("mrfoo.graph.complexity_score", "Score de complexidade/NOG", "complexity_score", {"type": "object", "properties": {"tenant_id": {"type": "string"}}, "required": ["tenant_id"]}),
    ("mrfoo.graph.combo_suggestions", "Sugestões de combos por co-ocorrência", "combo_suggestions", {"type": "object", "properties": {"tenant_id": {"type": "string"}, "timeslot": {"type": "string"}}, "required": ["tenant_id"]}),
    ("mrfoo.graph.new_item_suggestions", "Sugestões de novos itens", "new_item_suggestions", {"type": "object", "properties": {"tenant_id": {"type": "string"}, "max_items": {"type": "integer"}}, "required": ["tenant_id"]}),
]


class Command(BaseCommand):
    help = "Popula o MCP Registry com tools mrfoo.graph.* (Food Knowledge Graph)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seed mrfoo.graph tools (idempotente)..."))
        client = None
        try:
            client = ClientApp.objects.get(key="vitrinezap", is_active=True)
        except ClientApp.DoesNotExist:
            self.stdout.write(self.style.WARNING("ClientApp vitrinezap não encontrado; tools sem allowed_clients."))
        for name, description, action, input_schema in MRFOO_GRAPH_TOOLS:
            tool, created = Tool.objects.get_or_create(
                name=name,
                defaults={"description": description, "is_active": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"  Tool {name} criada"))
            if client and client not in tool.allowed_clients.all():
                tool.allowed_clients.add(client)
            config = {"action": action}
            tool_version, v_created = ToolVersion.objects.get_or_create(
                tool=tool,
                version="1.0.0",
                defaults={
                    "is_active": True,
                    "is_deprecated": False,
                    "runtime": "mrfoo_graph",
                    "config": config,
                    "input_schema": input_schema,
                    "output_schema": {"type": "object"},
                },
            )
            if v_created:
                self.stdout.write(self.style.SUCCESS(f"  ToolVersion 1.0.0 para {name} criada"))
            if not tool.current_version:
                tool.current_version = tool_version
                tool.save()
        self.stdout.write(self.style.SUCCESS("Seed mrfoo.graph concluído."))

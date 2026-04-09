"""
Seed: tool MCP para feedback de execução operacional do MrFoo.

Objetivo: permitir que o MrFoo chame o Core como VitrineZap (via MCP tools),
enviando um payload flexível (context + outcome) e armazenando em memória
semântica (vectorstore_service) para posterior retrieval no EOC/RAG.
"""

from django.core.management.base import BaseCommand

from app_mcp_tool_registry.models import ClientApp, Tool, ToolVersion


class Command(BaseCommand):
    help = "Popula o MCP Tool Registry com tool mrfoo.order_feedback (learning loop)"

    def handle(self, *args, **options):
        # 1) Garantir ClientApp mrfoo
        client, client_created = ClientApp.objects.get_or_create(
            key="mrfoo",
            defaults={
                "name": "MrFoo",
                "is_active": True,
            },
        )

        if client_created:
            self.stdout.write(self.style.SUCCESS('✓ ClientApp "mrfoo" criado'))

        if not client.api_key:
            client.generate_api_key()
            client.save()
            self.stdout.write(self.style.SUCCESS('✓ API key gerada para ClientApp "mrfoo"'))

        # 2) Criar Tool
        tool, _ = Tool.objects.get_or_create(
            name="mrfoo.order_feedback",
            defaults={
                "description": "Recebe feedback operacional de execução de pedido do MrFoo e armazena em memória semântica (learning loop).",
                "is_active": True,
            },
        )

        tool.is_active = True
        tool.save()

        # 3) Versão
        input_schema = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": ["string", "integer"], "description": "Tenant/empresa do MrFoo"},
                "pedido_id": {"type": ["string", "integer"], "description": "ID do pedido (no domínio do MrFoo)"},
                "context": {"type": "object", "description": "Contexto operacional (status, fila, tempo, etc.)"},
                "plan": {"type": "object", "description": "Plano/decisão sugerida pelo EOC (estrutura flexível)"},
                "outcome": {"type": "object", "description": "Resultado real da execução (sucesso, erro, latência, etc.)"},
                "success": {"type": "boolean"},
                "status": {"type": "string"},
            },
            "required": ["tenant_id", "pedido_id"],
        }

        output_schema = {
            "type": "object",
            "properties": {
                "status": {"type": "string"},
                "stored": {"type": "boolean"},
                "error": {"type": "string"},
            },
            "required": ["status"],
        }

        tool_version, created = ToolVersion.objects.get_or_create(
            tool=tool,
            version="1.0.0",
            defaults={
                "is_active": True,
                "is_deprecated": False,
                "runtime": "noop",
                "config": {},
                "input_schema": input_schema,
                "output_schema": output_schema,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS('✓ ToolVersion mrfoo.order_feedback@1.0.0 criada'))
        else:
            # Garantir que schema/config permaneçam coerentes
            tool_version.input_schema = input_schema
            tool_version.output_schema = output_schema
            tool_version.runtime = "noop"
            tool_version.is_active = True
            tool_version.save()
            self.stdout.write(self.style.WARNING('→ ToolVersion já existia; schema/config foram atualizados'))

        # 4) Setar current_version
        if not tool.current_version or tool.current_version_id != tool_version.id:
            tool.current_version = tool_version
            tool.save()

        # 5) Allowed clients: restringe ao mrfoo
        if client not in tool.allowed_clients.all():
            tool.allowed_clients.add(client)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS('API KEY DO ClientApp "mrfoo":'))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.WARNING(client.api_key))
        self.stdout.write(self.style.SUCCESS("=" * 60))


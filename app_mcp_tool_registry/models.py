"""
Models para o MCP Tool Registry
"""
from django.db import models
import secrets


class ClientApp(models.Model):
    """Aplicação cliente que pode chamar tools"""
    key = models.CharField(max_length=80, unique=True)  # ex: "vitrinezap"
    name = models.CharField(max_length=120)
    api_key = models.CharField(max_length=120, unique=True)  # gerar e armazenar
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'mcp_client_app'
        verbose_name = 'Client App'
        verbose_name_plural = 'Client Apps'

    def __str__(self):
        return self.key

    def generate_api_key(self):
        """Gera uma nova API key"""
        self.api_key = secrets.token_urlsafe(32)
        return self.api_key


class Tool(models.Model):
    """Tool MCP versionada"""
    name = models.CharField(max_length=160, unique=True)  # ex: "vitrinezap.analisar_produto"
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # controle "qual é a atual"
    current_version = models.ForeignKey(
        "ToolVersion",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    # quem pode usar
    allowed_clients = models.ManyToManyField(ClientApp, blank=True)

    class Meta:
        db_table = 'mcp_tool'
        verbose_name = 'Tool'
        verbose_name_plural = 'Tools'

    def __str__(self):
        return self.name


class ToolVersion(models.Model):
    """Versão específica de uma tool"""
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="versions")
    version = models.CharField(max_length=30)  # "1.0.0"
    is_active = models.BooleanField(default=True)
    is_deprecated = models.BooleanField(default=False)

    # contratos
    input_schema = models.JSONField(default=dict)
    output_schema = models.JSONField(default=dict)

    # runtime (como executa)
    runtime = models.CharField(
        max_length=40,
        choices=[
            ("noop", "Noop"),
            ("prompt", "Prompt"),
            ("openmind_http", "OpenMind HTTP"),
            ("pipeline", "Pipeline"),
            ("ddf", "DDF"),
        ],
        default="noop",
    )

    # configs do runtime (modelo, temperatura, url de serviço etc.)
    config = models.JSONField(default=dict)

    # opcional: referência de prompt/template
    prompt_ref = models.CharField(max_length=160, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mcp_tool_version'
        verbose_name = 'Tool Version'
        verbose_name_plural = 'Tool Versions'
        unique_together = ("tool", "version")

    def __str__(self):
        return f"{self.tool.name}@{self.version}"


class ToolCallLog(models.Model):
    """Log de chamadas de tools para auditoria"""
    request_id = models.CharField(max_length=64, db_index=True)
    tool = models.CharField(max_length=160)
    version = models.CharField(max_length=30)

    client_key = models.CharField(max_length=80, blank=True)
    ok = models.BooleanField(default=False)
    status_code = models.IntegerField(default=200)

    latency_ms = models.IntegerField(default=0)

    input_payload = models.JSONField(null=True, blank=True)
    output_payload = models.JSONField(null=True, blank=True)
    error_payload = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mcp_tool_call_log'
        verbose_name = 'Tool Call Log'
        verbose_name_plural = 'Tool Call Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.tool}@{self.version} - {self.request_id}"


import uuid
from django.db import models
from django.utils import timezone


class InboundEventStatus(models.TextChoices):
    RECEIVED = "RECEIVED", "Received"
    ENQUEUED = "ENQUEUED", "Enqueued"
    PROCESSING = "PROCESSING", "Processing"
    PROCESSED = "PROCESSED", "Processed"
    FAILED = "FAILED", "Failed"


class InboundEvent(models.Model):
    """
    Event sourcing leve: guarda o evento bruto + status.
    Idempotência é garantida por event_id único + lock Redis nas tasks.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=128, unique=True, db_index=True)
    source = models.CharField(max_length=64, db_index=True)
    payload_json = models.JSONField(default=dict, blank=True)

    received_at = models.DateTimeField(default=timezone.now, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=24,
        choices=InboundEventStatus.choices,
        default=InboundEventStatus.RECEIVED,
        db_index=True,
    )
    error_message = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-received_at"]

    def __str__(self) -> str:
        return f"InboundEvent(event_id={self.event_id}, source={self.source}, status={self.status})"


class DecisionLog(models.Model):
    """
    Memória de decisões do flow cognitivo (contexto → decisão → resultado).
    Acoplado ao pipeline atual; não substitui ToolCallLog nem cache semântico.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.CharField(max_length=128, db_index=True)
    source = models.CharField(max_length=64, default="task_queue_flow", db_index=True)

    contexto_json = models.JSONField(default=dict, blank=True)
    decisao_json = models.JSONField(default=dict, blank=True)
    resultado_json = models.JSONField(default=dict, blank=True)

    recorded_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return f"DecisionLog(event_id={self.event_id}, source={self.source})"


class DecisionFeedbackRecord(models.Model):
    """
    Memória de decisão (Fase 2): compara o previsto (risk/expected) com o outcome operacional.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trace_id = models.CharField(max_length=128, db_index=True)
    tenant_id = models.CharField(max_length=64, blank=True, db_index=True)
    source = models.CharField(max_length=64, db_index=True)
    decision_action = models.CharField(max_length=128)

    decision_json = models.JSONField(default=dict, blank=True)
    predicted_json = models.JSONField(default=dict, blank=True)
    outcome_json = models.JSONField(default=dict, blank=True)

    was_effective = models.BooleanField(null=True, blank=True)
    impact_score = models.FloatField(null=True, blank=True)
    decision_score_posterior = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    evaluated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"DecisionFeedback({self.trace_id}, {self.decision_action})"


class CognitivePatternMemory(models.Model):
    """
    Fase 3 — memória de padrões detectados (auditoria / replay).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=64, db_index=True)
    trace_id = models.CharField(max_length=128, db_index=True, blank=True)
    pattern_key = models.CharField(max_length=128, db_index=True)
    confidence = models.FloatField(default=0.0)
    signals_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"CognitivePatternMemory({self.pattern_key}, {self.tenant_id})"


class AutonomyActionLog(models.Model):
    """
    Fase 3 — proposta → DecisionEngine → execução (ou bloqueio).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=64, db_index=True)
    trace_id = models.CharField(max_length=128, db_index=True)
    proposal_key = models.CharField(max_length=128)
    mcp_tool = models.CharField(max_length=128, blank=True)
    decision_json = models.JSONField(default=dict, blank=True)
    autonomy_level = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=32, db_index=True)
    acp_task_id = models.CharField(max_length=64, blank=True)
    outcome_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"AutonomyActionLog({self.proposal_key}, {self.status})"


class StrategyFeedbackRecord(models.Model):
    """
    Fase 4 — feedback estratégico: impacto previsto vs realizado.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=64, db_index=True)
    strategy_key = models.CharField(max_length=128, db_index=True)
    proposal_id = models.CharField(max_length=128, blank=True)
    predicted_impact = models.FloatField(default=0.0)
    realized_impact = models.FloatField(null=True, blank=True)
    variance = models.FloatField(null=True, blank=True)
    payload_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"StrategyFeedback({self.strategy_key}, {self.tenant_id})"

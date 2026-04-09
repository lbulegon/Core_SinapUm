"""
Modelos Django para Architecture Intelligence Service.
Persistência PostgreSQL via migrations.
"""
from django.db import models

class ArchitectureCycle(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    cycle_type = models.CharField(max_length=64)
    state = models.CharField(max_length=32)
    artifact_content = models.TextField()
    artifact_type = models.CharField(max_length=64, default="document")
    artifact_domain_id = models.CharField(max_length=255, null=True, blank=True)
    artifact_metadata = models.JSONField(default=dict, blank=True)
    trace_id = models.CharField(max_length=255, null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "architecture_cycles"
        ordering = ["-created_at"]

class ArchitectureStageRun(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    cycle = models.ForeignKey(ArchitectureCycle, on_delete=models.CASCADE, related_name="stage_runs", db_column="cycle_id")
    stage = models.CharField(max_length=64)
    state = models.CharField(max_length=32)
    input_content = models.TextField()
    output_content = models.TextField(default="")
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "architecture_stage_runs"
        ordering = ["created_at"]

class ArchitectureDecisionLog(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    cycle = models.ForeignKey(ArchitectureCycle, on_delete=models.CASCADE, related_name="decisions", db_column="cycle_id")
    stage = models.CharField(max_length=64)
    decision = models.TextField()
    rationale = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "architecture_decisions"
        ordering = ["-created_at"]

class ArchitectureRisk(models.Model):
    id = models.CharField(max_length=36, primary_key=True, editable=False)
    cycle = models.ForeignKey(ArchitectureCycle, on_delete=models.CASCADE, related_name="risks", db_column="cycle_id")
    stage = models.CharField(max_length=64)
    risk_description = models.TextField()
    severity = models.CharField(max_length=32)
    mitigation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "architecture_risks"
        ordering = ["-created_at"]

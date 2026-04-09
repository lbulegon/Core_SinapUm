"""
Models do Creative Engine - apenas persistência, sem lógica cognitiva
"""
import uuid
from django.db import models
from django.utils import timezone


class CreativeAsset(models.Model):
    """Asset de criativo (imagem, texto, etc)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creative_id = models.CharField(max_length=128, db_index=True)
    variant_id = models.CharField(max_length=128, db_index=True)
    product_id = models.CharField(max_length=128, db_index=True)
    shopper_id = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    channel = models.CharField(max_length=32, db_index=True)
    strategy = models.CharField(max_length=64, db_index=True)
    image_url = models.URLField(null=True, blank=True)
    text_short = models.TextField(null=True, blank=True)
    text_medium = models.TextField(null=True, blank=True)
    text_long = models.TextField(null=True, blank=True)
    discourse = models.JSONField(default=dict, blank=True)
    ctas = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'creative_asset'
        indexes = [
            models.Index(fields=['creative_id', 'variant_id']),
            models.Index(fields=['product_id', 'shopper_id']),
            models.Index(fields=['channel', 'strategy']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.creative_id} - {self.variant_id}"


class CreativePerformance(models.Model):
    """Performance de criativo (eventos)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    variant_id = models.CharField(max_length=128, db_index=True)
    creative_id = models.CharField(max_length=128, db_index=True)
    product_id = models.CharField(max_length=128, db_index=True)
    shopper_id = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    event_type = models.CharField(max_length=64, db_index=True)
    event_data = models.JSONField(default=dict, blank=True)
    correlation_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'creative_performance'
        indexes = [
            models.Index(fields=['variant_id', 'event_type']),
            models.Index(fields=['product_id', 'shopper_id']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.variant_id} - {self.event_type} - {self.created_at}"


class CreativeScore(models.Model):
    """Score agregado de performance por variante"""
    variant_id = models.CharField(max_length=128, unique=True, primary_key=True)
    creative_id = models.CharField(max_length=128, db_index=True)
    product_id = models.CharField(max_length=128, db_index=True)
    channel = models.CharField(max_length=32, db_index=True)
    strategy = models.CharField(max_length=64, db_index=True)
    response_rate = models.FloatField(default=0.0)
    interest_rate = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)
    engagement_score = models.FloatField(default=0.0)
    confidence_index = models.FloatField(default=0.0)
    total_views = models.IntegerField(default=0)
    total_responses = models.IntegerField(default=0)
    total_interests = models.IntegerField(default=0)
    total_orders = models.IntegerField(default=0)
    total_conversions = models.IntegerField(default=0)
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'creative_score'
        indexes = [
            models.Index(fields=['product_id', 'channel']),
            models.Index(fields=['strategy', 'engagement_score']),
        ]
        ordering = ['-engagement_score']
    
    def __str__(self):
        return f"{self.variant_id} - Score: {self.engagement_score:.2f}"


class CreativeJob(models.Model):
    """
    Job assíncrono de geração de criativos (fluxo Kwai/Tamo)
    Usuário envia foto → processamento em background → múltiplas variações
    """
    class JobStatus(models.TextChoices):
        QUEUED = 'queued', 'Na fila'
        PROCESSING = 'processing', 'Processando'
        COMPLETED = 'completed', 'Concluído'
        FAILED = 'failed', 'Falhou'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shopper_id = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    product_id = models.CharField(max_length=128, db_index=True, null=True, blank=True)

    # Input
    image_path = models.CharField(max_length=512, help_text='Caminho da imagem de entrada')
    image_url = models.URLField(null=True, blank=True, help_text='URL da imagem (alternativa)')

    # Status
    status = models.CharField(
        max_length=20,
        choices=JobStatus.choices,
        default=JobStatus.QUEUED,
        db_index=True
    )
    stage = models.CharField(max_length=64, blank=True, help_text='Etapa atual: analyzing, removing_bg, generating')
    progress = models.IntegerField(default=0, help_text='0-100')
    description = models.TextField(blank=True, help_text='Descrição gerada do produto')
    error_message = models.TextField(blank=True, null=True)

    # Metadados
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'creative_job'
        ordering = ['-created_at']

    def __str__(self):
        return f"Job {self.id} - {self.get_status_display()}"


class CreativeJobOutput(models.Model):
    """Output gerado por um CreativeJob (imagem lifestyle, clean shot, etc)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(
        CreativeJob,
        on_delete=models.CASCADE,
        related_name='outputs'
    )

    style = models.CharField(max_length=64, db_index=True)  # lifestyle, clean_product, contextual
    template_id = models.CharField(max_length=64, blank=True)
    image_url = models.URLField()
    thumbnail_url = models.URLField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'creative_job_output'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.job_id} - {self.style}"

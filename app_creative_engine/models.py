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

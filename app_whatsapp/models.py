"""
Models do WhatsApp Gateway
"""
import uuid
from django.db import models
from django.utils import timezone


class AppWhatsappEvent(models.Model):
    """Evento canônico do WhatsApp Gateway"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_id = models.UUIDField(unique=True, default=uuid.uuid4, db_index=True)
    ts = models.DateTimeField(auto_now_add=True, db_index=True)
    provider = models.CharField(max_length=32, db_index=True)
    instance_key = models.CharField(max_length=128, db_index=True)
    type = models.CharField(max_length=64, db_index=True)  # EVENT TYPE
    shopper_id = models.CharField(max_length=128, null=True, blank=True, db_index=True)
    correlation_id = models.UUIDField(null=True, blank=True)
    data = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'app_whatsapp_event'
        indexes = [
            models.Index(fields=['instance_key', 'ts']),
            models.Index(fields=['provider', 'type']),
            models.Index(fields=['shopper_id', 'ts']),
        ]
        ordering = ['-ts']
        verbose_name = 'WhatsApp Event'
        verbose_name_plural = 'WhatsApp Events'
    
    def __str__(self):
        return f"{self.type} - {self.instance_key} - {self.ts}"


class AppWhatsappInstance(models.Model):
    """Instância WhatsApp"""
    
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('connecting', 'Connecting'),
        ('connected', 'Connected'),
        ('closed', 'Closed'),
    ]
    
    instance_key = models.CharField(max_length=128, unique=True, primary_key=True)
    provider = models.CharField(max_length=32)
    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        default='created',
        db_index=True
    )
    last_qr = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'app_whatsapp_instance'
        indexes = [
            models.Index(fields=['provider', 'status']),
        ]
        ordering = ['-created_at']
        verbose_name = 'WhatsApp Instance'
        verbose_name_plural = 'WhatsApp Instances'
    
    def __str__(self):
        return f"{self.instance_key} - {self.provider} - {self.status}"

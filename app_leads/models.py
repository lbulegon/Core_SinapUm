"""
Lead Registry - Sistema central de captação de leads
Reutilizável por todos os projetos: VitrineZap, MotoPro, Eventix, MrFoo, etc.
"""
from django.db import models
from django.utils import timezone


class ProjectCredential(models.Model):
    """
    Credenciais de projetos autorizados a publicar leads no Core.
    Cada projeto possui um project_key e um project_secret para assinatura HMAC.
    """
    project_key = models.CharField(
        max_length=50,
        unique=True,
        help_text="Identificador único do projeto (ex: vitrinezap, motopro, eventix)"
    )
    project_secret = models.CharField(
        max_length=255,
        help_text="Secret para geração de assinatura HMAC (armazenar de forma segura)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Se False, o projeto não pode mais publicar leads"
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Credencial de Projeto"
        verbose_name_plural = "Credenciais de Projetos"
        indexes = [
            models.Index(fields=["project_key"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.project_key} ({'ativo' if self.is_active else 'inativo'})"


class Lead(models.Model):
    """
    Lead centralizado - evento humano de interesse.
    Não pertence a nenhum projeto específico, mas é gerado por eles.
    """
    LEAD_STATUS_CHOICES = [
        ("new", "Novo"),
        ("qualified", "Qualificado"),
        ("activated", "Ativado"),
        ("dormant", "Inativo"),
    ]

    # Dados básicos do lead
    nome = models.CharField(max_length=120)
    email = models.EmailField()
    whatsapp = models.CharField(max_length=32)
    cidade = models.CharField(max_length=120, blank=True)

    # Multi-sistema (reuso total)
    source_system = models.CharField(
        max_length=50,
        default="unknown",
        help_text="Sistema que gerou o lead (vitrinezap, motopro, eventix, etc.)"
    )
    source_entrypoint = models.CharField(
        max_length=80,
        blank=True,
        help_text="Ponto de entrada (home, modal, landing, etc.)"
    )
    source_context = models.CharField(
        max_length=80,
        blank=True,
        help_text="Contexto específico (lista_antecipada, cadastro, download, etc.)"
    )

    # UTM parameters
    utm_source = models.CharField(max_length=120, blank=True)
    utm_campaign = models.CharField(max_length=120, blank=True)
    utm_medium = models.CharField(max_length=120, blank=True)
    utm_content = models.CharField(max_length=120, blank=True)

    # Lifecycle
    lead_status = models.CharField(
        max_length=30,
        choices=LEAD_STATUS_CHOICES,
        default="new"
    )
    is_opt_out = models.BooleanField(
        default=False,
        help_text="Se True, o lead optou por não receber comunicações"
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["whatsapp"]),
            models.Index(fields=["source_system"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["lead_status"]),
        ]

    def __str__(self):
        return f"{self.nome} • {self.whatsapp} • {self.source_system}"


class LeadEvent(models.Model):
    """
    Eventos de auditoria para cada lead.
    Registra todas as interações e mudanças de estado.
    """
    EVENT_TYPE_CHOICES = [
        ("created", "Criado"),
        ("updated", "Atualizado"),
        ("rejected", "Rejeitado"),
        ("rate_limited", "Rate Limited"),
        ("opt_out", "Opt-out"),
    ]

    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name="events",
        null=True,
        blank=True,
        help_text="Pode ser None para eventos de rejeição/rate_limit antes da criação do lead"
    )
    event_type = models.CharField(
        max_length=40,
        choices=EVENT_TYPE_CHOICES
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Evento de Lead"
        verbose_name_plural = "Eventos de Leads"
        indexes = [
            models.Index(fields=["lead", "created_at"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} • {self.lead_id} • {self.created_at.strftime('%Y-%m-%d %H:%M')}"


"""
Open Finance Gateway Models.
"""
import uuid
from django.db import models
from django.utils import timezone


class OF_Consent(models.Model):
    """Consentimento Open Finance."""
    ORIGIN_CHOICES = [
        ('paypi', 'PayPi'),
        ('motopro', 'MotoPro'),
        ('vitrinezap', 'VitrineZap'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
        ('REVOKED', 'REVOKED'),
        ('EXPIRED', 'EXPIRED'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255, db_index=True)
    origin_system = models.CharField(max_length=32, choices=ORIGIN_CHOICES, default='other')
    provider = models.CharField(max_length=64, default='stub')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    scope = models.JSONField(default=dict)
    external_consent_id = models.CharField(max_length=255, blank=True, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'of_consent'
        ordering = ['-created_at']

    def __str__(self):
        return f"OF_Consent({self.id}, {self.user_id}, {self.status})"


class OF_Credential(models.Model):
    """Credenciais criptografadas (tokens)."""
    consent = models.OneToOneField(
        OF_Consent,
        on_delete=models.CASCADE,
        related_name='credential'
    )
    access_token_enc = models.TextField()
    refresh_token_enc = models.TextField()
    token_expires_at = models.DateTimeField()
    key_version = models.IntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'of_credential'

    def __str__(self):
        return f"OF_Credential(consent={self.consent_id})"


class OF_Account(models.Model):
    """Conta bancária vinculada ao consentimento."""
    consent = models.ForeignKey(
        OF_Consent,
        on_delete=models.CASCADE,
        related_name='accounts'
    )
    external_account_id = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=64, default='checking')
    currency = models.CharField(max_length=3, default='BRL')
    masked_number = models.CharField(max_length=32, default='')
    owner_name = models.CharField(max_length=255, null=True, blank=True)
    owner_doc = models.CharField(max_length=32, null=True, blank=True)
    owner_match_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'of_account'
        ordering = ['created_at']
        unique_together = [['consent', 'external_account_id']]

    def __str__(self):
        return f"OF_Account({self.external_account_id}, {self.masked_number})"


class OF_Transaction(models.Model):
    """Transação bancária."""
    DIRECTION_CHOICES = [
        ('IN', 'IN'),
        ('OUT', 'OUT'),
    ]

    account = models.ForeignKey(
        OF_Account,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    external_tx_id = models.CharField(max_length=255, db_index=True)
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    direction = models.CharField(max_length=4, choices=DIRECTION_CHOICES)
    description = models.TextField(blank=True)
    description_hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'of_transaction'
        ordering = ['-date']
        unique_together = [['account', 'external_tx_id']]
        indexes = [
            models.Index(fields=['account', 'date']),
        ]

    def __str__(self):
        return f"OF_Transaction({self.external_tx_id}, {self.amount} {self.direction})"


class OF_DataSnapshot(models.Model):
    """Snapshot de dados (auditoria/histórico)."""
    SNAPSHOT_TYPES = [
        ('ACCOUNTS', 'ACCOUNTS'),
        ('TRANSACTIONS', 'TRANSACTIONS'),
        ('PROFILE', 'PROFILE'),
    ]

    consent = models.ForeignKey(
        OF_Consent,
        on_delete=models.CASCADE,
        related_name='snapshots'
    )
    snapshot_type = models.CharField(max_length=32, choices=SNAPSHOT_TYPES)
    payload = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'of_data_snapshot'
        ordering = ['-created_at']


class OF_AuditLog(models.Model):
    """Log append-only de ações sensíveis."""
    ACTION_CHOICES = [
        ('consent_create', 'consent_create'),
        ('consent_approved', 'consent_approved'),
        ('token_refresh', 'token_refresh'),
        ('sync_accounts', 'sync_accounts'),
        ('sync_transactions', 'sync_transactions'),
        ('profile_view', 'profile_view'),
    ]

    consent = models.ForeignKey(
        OF_Consent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    user_id = models.CharField(max_length=255, db_index=True)
    origin_system = models.CharField(max_length=32)
    action = models.CharField(max_length=64, choices=ACTION_CHOICES)
    meta = models.JSONField(default=dict)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'of_audit_log'
        ordering = ['-created_at']

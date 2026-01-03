"""
Models para integração iFood → MrFoo
Armazena lojas, tokens OAuth, histórico de sincronização e dados normalizados.
"""
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import json


class IfoodStore(models.Model):
    """
    Representa uma loja/estabelecimento no iFood.
    """
    nome = models.CharField(max_length=120, help_text="Nome da loja")
    cnpj = models.CharField(max_length=18, blank=True, null=True, help_text="CNPJ da loja")
    
    # Identidade no iFood
    ifood_merchant_id = models.CharField(
        max_length=80, 
        unique=True,
        help_text="ID único da loja no iFood (merchantId ou storeId)"
    )
    
    ativo = models.BooleanField(default=True, help_text="Loja ativa para sincronização")
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ifood_store'
        verbose_name = 'Loja iFood'
        verbose_name_plural = 'Lojas iFood'
        ordering = ['nome']
    
    def __str__(self):
        return f"{self.nome} ({self.ifood_merchant_id})"
    
    @property
    def has_valid_token(self):
        """Verifica se a loja possui token OAuth válido"""
        try:
            token = self.oauth_token
            return token and not token.is_expired()
        except IfoodOAuthToken.DoesNotExist:
            return False


class IfoodOAuthToken(models.Model):
    """
    Tokens OAuth 2.0 por loja (access_token, refresh_token).
    IMPORTANTE: Tokens devem ser criptografados em produção.
    """
    store = models.OneToOneField(
        IfoodStore,
        on_delete=models.CASCADE,
        related_name='oauth_token',
        help_text="Loja associada ao token"
    )
    
    # Tokens (devem ser criptografados em produção)
    access_token = models.TextField(help_text="Access token OAuth (criptografado em produção)")
    refresh_token = models.TextField(help_text="Refresh token OAuth (criptografado em produção)")
    token_type = models.CharField(max_length=20, default="Bearer")
    
    # Expiração
    expires_at = models.DateTimeField(help_text="Data/hora de expiração do access_token")
    
    # Escopos
    scope = models.TextField(blank=True, null=True, help_text="Escopos OAuth concedidos")
    
    # Metadados
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ifood_oauth_token'
        verbose_name = 'Token OAuth iFood'
        verbose_name_plural = 'Tokens OAuth iFood'
    
    def __str__(self):
        return f"Token para {self.store.nome} (expira: {self.expires_at})"
    
    def is_expired(self) -> bool:
        """Verifica se o token está expirado"""
        return timezone.now() >= self.expires_at
    
    def needs_refresh(self, buffer_minutes: int = 5) -> bool:
        """Verifica se o token precisa ser renovado (com buffer de segurança)"""
        buffer_time = timezone.timedelta(minutes=buffer_minutes)
        return timezone.now() >= (self.expires_at - buffer_time)


class IfoodSyncRun(models.Model):
    """
    Histórico de execuções de sincronização (orders, finance, catalog).
    """
    SYNC_KINDS = [
        ('orders', 'Pedidos'),
        ('financial', 'Financeiro'),
        ('catalog', 'Catálogo'),
    ]
    
    store = models.ForeignKey(
        IfoodStore,
        on_delete=models.CASCADE,
        related_name='sync_runs',
        help_text="Loja sincronizada"
    )
    
    kind = models.CharField(
        max_length=40,
        choices=SYNC_KINDS,
        help_text="Tipo de sincronização"
    )
    
    started_at = models.DateTimeField(auto_now_add=True, help_text="Início da sincronização")
    finished_at = models.DateTimeField(blank=True, null=True, help_text="Fim da sincronização")
    
    ok = models.BooleanField(default=False, help_text="Sincronização bem-sucedida")
    
    items_ingested = models.IntegerField(
        default=0,
        help_text="Quantidade de itens processados/inseridos"
    )
    
    error = models.TextField(blank=True, null=True, help_text="Mensagem de erro (se houver)")
    
    # Metadados adicionais (JSON)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Metadados adicionais da sincronização (JSON)"
    )
    
    class Meta:
        db_table = 'ifood_sync_run'
        verbose_name = 'Execução de Sincronização'
        verbose_name_plural = 'Execuções de Sincronização'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['store', 'kind', '-started_at']),
            models.Index(fields=['ok', '-started_at']),
        ]
    
    def __str__(self):
        status = "✓" if self.ok else "✗"
        return f"{status} {self.kind} - {self.store.nome} ({self.started_at})"
    
    @property
    def duration_seconds(self):
        """Duração da sincronização em segundos"""
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None


class MrfooOrder(models.Model):
    """
    Pedidos normalizados do iFood para consumo do Dashboard MrFoo.
    """
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pendente'),
        ('CONFIRMED', 'Confirmado'),
        ('PREPARING', 'Preparando'),
        ('READY', 'Pronto'),
        ('DISPATCHED', 'Despachado'),
        ('DELIVERED', 'Entregue'),
        ('CANCELLED', 'Cancelado'),
    ]
    
    store = models.ForeignKey(
        IfoodStore,
        on_delete=models.CASCADE,
        related_name='orders',
        help_text="Loja que recebeu o pedido"
    )
    
    # IDs
    order_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="ID único do pedido no iFood"
    )
    
    # Dados do pedido
    created_at = models.DateTimeField(help_text="Data/hora de criação do pedido")
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='PENDING',
        help_text="Status atual do pedido"
    )
    
    total_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor total do pedido"
    )
    
    channel = models.CharField(
        max_length=20,
        default='ifood',
        help_text="Canal de origem (ifood, delivery, etc.)"
    )
    
    # Dados adicionais (JSON)
    raw_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dados brutos do pedido (JSON completo do iFood)"
    )
    
    # Metadados
    synced_at = models.DateTimeField(auto_now_add=True, help_text="Data/hora da sincronização")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mrfoo_order'
        verbose_name = 'Pedido MrFoo'
        verbose_name_plural = 'Pedidos MrFoo'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', '-created_at']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['channel', '-created_at']),
        ]
    
    def __str__(self):
        return f"Pedido {self.order_id} - {self.store.nome} - R$ {self.total_value}"


class MrfooPayout(models.Model):
    """
    Repasses financeiros normalizados do iFood para consumo do Dashboard MrFoo.
    """
    store = models.ForeignKey(
        IfoodStore,
        on_delete=models.CASCADE,
        related_name='payouts',
        help_text="Loja que recebeu o repasse"
    )
    
    # IDs
    payout_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="ID único do repasse no iFood"
    )
    
    # Período de referência
    reference_period = models.CharField(
        max_length=20,
        help_text="Período de referência (ex: '2024-01')"
    )
    
    # Valores financeiros
    gross = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor bruto"
    )
    
    fees = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Taxas descontadas"
    )
    
    net = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor líquido (bruto - taxas)"
    )
    
    channel = models.CharField(
        max_length=20,
        default='ifood',
        help_text="Canal de origem"
    )
    
    # Dados adicionais (JSON)
    raw_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="Dados brutos do repasse (JSON completo do iFood)"
    )
    
    # Metadados
    synced_at = models.DateTimeField(auto_now_add=True, help_text="Data/hora da sincronização")
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mrfoo_payout'
        verbose_name = 'Repasse MrFoo'
        verbose_name_plural = 'Repasses MrFoo'
        ordering = ['-reference_period', 'store']
        indexes = [
            models.Index(fields=['store', '-reference_period']),
            models.Index(fields=['channel', '-reference_period']),
        ]
    
    def __str__(self):
        return f"Repasse {self.payout_id} - {self.store.nome} - R$ {self.net} ({self.reference_period})"


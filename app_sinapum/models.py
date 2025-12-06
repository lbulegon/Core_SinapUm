from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
try:
    from django.contrib.postgres.fields import JSONField as PostgresJSONField
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
import json


class Estabelecimento(models.Model):
    """Estabelecimento onde o produto foi comprado"""
    nome = models.CharField(max_length=200)
    endereco = models.TextField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estabelecimento"
        verbose_name_plural = "Estabelecimentos"
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Campanha(models.Model):
    """Campanha relacionada à viagem de compras"""
    nome = models.CharField(max_length=200)
    data_registro = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Campanha"
        verbose_name_plural = "Campanhas"
        ordering = ['-data_registro']

    def __str__(self):
        return self.nome


class Shopper(models.Model):
    """Shopper responsável pela compra"""
    nome = models.CharField(max_length=200)
    pais = models.CharField(max_length=100)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Shopper"
        verbose_name_plural = "Shoppers"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.pais})"


class ProdutoGenericoCatalogo(models.Model):
    """Produto genérico do catálogo (sem especificações de volume/tipo)"""
    nome = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100)
    variantes = models.JSONField(default=list, blank=True, help_text="Lista de variantes do produto (ex: ['50ml', 'Parfum'])")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto Genérico do Catálogo"
        verbose_name_plural = "Produtos Genéricos do Catálogo"
        ordering = ['marca', 'nome']
        unique_together = [['nome', 'marca', 'categoria', 'subcategoria']]

    def __str__(self):
        return f"{self.marca} - {self.nome}"


class Produto(models.Model):
    """Produto específico com todas as informações detalhadas"""
    produto_generico = models.ForeignKey(
        ProdutoGenericoCatalogo,
        on_delete=models.CASCADE,
        related_name='produtos',
        null=True,
        blank=True,
        help_text="Produto genérico relacionado ao catálogo"
    )
    nome = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    descricao = models.TextField()
    categoria = models.CharField(max_length=100)
    subcategoria = models.CharField(max_length=100)
    familia_olfativa = models.CharField(max_length=100, null=True, blank=True)
    volume_ml = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0)])
    tipo = models.CharField(max_length=100, null=True, blank=True)
    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True)
    imagens = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de nomes de arquivos de imagens do produto"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ['marca', 'nome']

    def __str__(self):
        return f"{self.marca} - {self.nome}"


class ProdutoViagem(models.Model):
    """Informações financeiras e de viagem relacionadas ao produto"""
    produto = models.OneToOneField(
        Produto,
        on_delete=models.CASCADE,
        related_name='produto_viagem'
    )
    estabelecimento = models.ForeignKey(
        Estabelecimento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos_viagem'
    )
    campanha = models.ForeignKey(
        Campanha,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos_viagem'
    )
    shopper = models.ForeignKey(
        Shopper,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos_viagem'
    )
    preco_compra_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    preco_compra_brl = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    margem_lucro_percentual = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        help_text="Margem de lucro em percentual"
    )
    preco_venda_usd = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    preco_venda_brl = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produto Viagem"
        verbose_name_plural = "Produtos Viagem"
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.produto.nome} - {self.preco_venda_brl} BRL"

    def calcular_preco_venda_brl(self):
        """Calcula o preço de venda em BRL baseado no preço de compra e margem"""
        return self.preco_compra_brl * (1 + self.margem_lucro_percentual / 100)

    def calcular_preco_venda_usd(self):
        """Calcula o preço de venda em USD baseado no preço de compra e margem"""
        return self.preco_compra_usd * (1 + self.margem_lucro_percentual / 100)


class CadastroMeta(models.Model):
    """Metadados sobre o cadastro do produto (fonte, IA, confiança, etc)"""
    produto = models.OneToOneField(
        Produto,
        on_delete=models.CASCADE,
        related_name='cadastro_meta'
    )
    capturado_por = models.CharField(max_length=200, help_text="Sistema/IA que capturou os dados")
    data_captura = models.DateTimeField()
    fonte = models.TextField(help_text="Fonte dos dados (ex: Fotos tiradas na loja)")
    confianca_da_leitura = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Confiança da leitura (0.0 a 1.0)"
    )
    detalhes_rotulo = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detalhes do rótulo (frase, origem, duração, etc)"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cadastro Meta"
        verbose_name_plural = "Cadastros Meta"
        ordering = ['-data_captura']

    def __str__(self):
        return f"Meta: {self.produto.nome} - {self.confianca_da_leitura}"


class ProdutoJSON(models.Model):
    """Model para armazenar produtos completos em formato JSON (PostgreSQL JSONB ou SQLite JSON)"""
    dados_json = models.JSONField(help_text="Dados completos do produto no formato modelo.json")
    nome_produto = models.CharField(max_length=500, db_index=True, help_text="Nome do produto para busca rápida")
    marca = models.CharField(max_length=200, db_index=True, null=True, blank=True)
    categoria = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True, db_index=True)
    imagem_original = models.CharField(max_length=500, null=True, blank=True, help_text="Nome do arquivo de imagem original")
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Produto JSON"
        verbose_name_plural = "Produtos JSON"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['nome_produto', 'marca']),
            models.Index(fields=['categoria']),
        ]
    
    def __str__(self):
        return f"{self.nome_produto} ({self.marca}) - {self.criado_em.strftime('%d/%m/%Y')}"
    
    def get_produto_data(self):
        """Retorna os dados do produto em formato dict"""
        if isinstance(self.dados_json, str):
            import json
            return json.loads(self.dados_json)
        return self.dados_json or {}

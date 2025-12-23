from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator
from django.core.exceptions import ValidationError
try:
    from django.contrib.postgres.fields import JSONField as PostgresJSONField
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
import json
import logging
from django.conf import settings
import base64
import hashlib

logger = logging.getLogger(__name__)

# Tentar importar cryptography, se não estiver disponível, usar encoding simples
try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    import warnings
    warnings.warn(
        "A biblioteca 'cryptography' não está instalada. "
        "As credenciais não serão criptografadas. "
        "Instale com: pip install cryptography>=41.0.0",
        ImportWarning
    )


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
    """Model para armazenar produtos completos em formato JSON (PostgreSQL JSONB)"""
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


class ServicoExterno(models.Model):
    """Model para armazenar credenciais e configurações de serviços externos contratados"""
    
    TIPO_SERVICO_CHOICES = [
        # Serviços de comunicação e API
        ('twilio', 'Twilio'),
        ('sendgrid', 'SendGrid'),
        ('telegram', 'Telegram Bot API'),
        ('whatsapp', 'WhatsApp Business API'),
        # Cloud e infraestrutura
        ('aws', 'AWS'),
        ('azure', 'Azure'),
        ('google', 'Google Cloud'),
        ('firebase', 'Firebase'),
        ('railway', 'Railway'),
        ('digitalocean', 'DigitalOcean'),
        ('linode', 'Linode'),
        # VPS e Hospedagem
        ('interserver', 'InterServer'),
        ('godaddy', 'GoDaddy'),
        ('namecheap', 'Namecheap'),
        ('hostgator', 'HostGator'),
        ('bluehost', 'Bluehost'),
        ('hostinger', 'Hostinger'),
        ('siteground', 'SiteGround'),
        ('dreamhost', 'DreamHost'),
        ('vultr', 'Vultr'),
        ('hetzner', 'Hetzner'),
        ('contabo', 'Contabo'),
        # Pagamentos
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('mercadopago', 'Mercado Pago'),
        # Redes Sociais
        ('facebook', 'Facebook API'),
        ('instagram', 'Instagram API'),
        # IA e Machine Learning
        ('openai', 'OpenAI'),
        # Outros
        ('outro', 'Outro'),
    ]
    
    AMBIENTE_CHOICES = [
        ('desenvolvimento', 'Desenvolvimento'),
        ('homologacao', 'Homologação'),
        ('producao', 'Produção'),
    ]
    
    nome = models.CharField(
        max_length=200,
        help_text="Nome identificador do serviço (ex: Twilio Principal, Firebase Prod)"
    )
    tipo_servico = models.CharField(
        max_length=50,
        choices=TIPO_SERVICO_CHOICES,
        default='outro',
        help_text="Tipo de serviço contratado"
    )
    ambiente = models.CharField(
        max_length=20,
        choices=AMBIENTE_CHOICES,
        default='desenvolvimento',
        help_text="Ambiente de uso do serviço"
    )
    url_base = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL base do serviço (ex: https://api.twilio.com)"
    )
    usuario = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Usuário/Login para autenticação"
    )
    senha = models.TextField(
        blank=True,
        null=True,
        help_text="Senha/Token de autenticação (armazenado de forma criptografada)"
    )
    api_key = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="API Key do serviço"
    )
    api_secret = models.TextField(
        blank=True,
        null=True,
        help_text="API Secret (armazenado de forma criptografada)"
    )
    account_sid = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Account SID (para serviços como Twilio)"
    )
    auth_token = models.TextField(
        blank=True,
        null=True,
        help_text="Auth Token (armazenado de forma criptografada)"
    )
    # Campos específicos para VPS e Servidores
    ip_servidor = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="Endereço IP do servidor VPS"
    )
    porta_ssh = models.IntegerField(
        blank=True,
        null=True,
        default=22,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        help_text="Porta SSH do servidor (padrão: 22)"
    )
    usuario_ssh = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Usuário SSH para acesso ao servidor"
    )
    senha_ssh = models.TextField(
        blank=True,
        null=True,
        help_text="Senha SSH (armazenado de forma criptografada)"
    )
    chave_privada_ssh = models.TextField(
        blank=True,
        null=True,
        help_text="Chave privada SSH (armazenado de forma criptografada)"
    )
    url_painel_controle = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="URL do painel de controle (cPanel, Plesk, etc)"
    )
    usuario_painel = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Usuário do painel de controle"
    )
    senha_painel = models.TextField(
        blank=True,
        null=True,
        help_text="Senha do painel de controle (armazenado de forma criptografada)"
    )
    sistema_operacional = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Sistema operacional do servidor (ex: Ubuntu 22.04, CentOS 7)"
    )
    porta_ftp = models.IntegerField(
        blank=True,
        null=True,
        default=21,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        help_text="Porta FTP (padrão: 21)"
    )
    usuario_ftp = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Usuário FTP"
    )
    senha_ftp = models.TextField(
        blank=True,
        null=True,
        help_text="Senha FTP (armazenado de forma criptografada)"
    )
    porta_mysql = models.IntegerField(
        blank=True,
        null=True,
        default=3306,
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        help_text="Porta MySQL/MariaDB (padrão: 3306)"
    )
    usuario_mysql = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Usuário do banco de dados MySQL"
    )
    senha_mysql = models.TextField(
        blank=True,
        null=True,
        help_text="Senha do banco de dados MySQL (armazenado de forma criptografada)"
    )
    nome_banco_dados = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Nome do banco de dados"
    )
    credenciais_adicionais = models.JSONField(
        default=dict,
        blank=True,
        help_text="Credenciais adicionais em formato JSON (ex: project_id, database_url, domain, etc)"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o serviço está ativo e sendo usado"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre o serviço e credenciais"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Serviço Externo"
        verbose_name_plural = "Serviços Externos"
        ordering = ['tipo_servico', 'ambiente', 'nome']
        unique_together = [['tipo_servico', 'ambiente', 'nome']]
    
    def __str__(self):
        status = "✓" if self.ativo else "✗"
        return f"{status} {self.get_tipo_servico_display()} - {self.nome} ({self.get_ambiente_display()})"
    
    def _get_encryption_key(self):
        """Gera uma chave de criptografia baseada no SECRET_KEY do Django"""
        secret_key = settings.SECRET_KEY.encode()
        # Gera uma chave Fernet a partir do SECRET_KEY
        key = base64.urlsafe_b64encode(hashlib.sha256(secret_key).digest())
        return key
    
    def _encrypt(self, value):
        """Criptografa um valor"""
        if not value:
            return value
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            encrypted = f.encrypt(value.encode())
            return encrypted.decode()
        except Exception:
            # Se falhar a criptografia, retorna o valor original (não recomendado em produção)
            return value
    
    def _decrypt(self, encrypted_value):
        """Descriptografa um valor"""
        if not encrypted_value:
            return encrypted_value
        try:
            key = self._get_encryption_key()
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_value.encode())
            return decrypted.decode()
        except Exception:
            # Se falhar, retorna o valor original
            return encrypted_value
    
    def get_senha_decrypted(self):
        """Retorna a senha descriptografada"""
        return self._decrypt(self.senha) if self.senha else None
    
    def get_api_secret_decrypted(self):
        """Retorna o API Secret descriptografado"""
        return self._decrypt(self.api_secret) if self.api_secret else None
    
    def get_auth_token_decrypted(self):
        """Retorna o Auth Token descriptografado"""
        return self._decrypt(self.auth_token) if self.auth_token else None
    
    def get_senha_ssh_decrypted(self):
        """Retorna a senha SSH descriptografada"""
        return self._decrypt(self.senha_ssh) if self.senha_ssh else None
    
    def get_chave_privada_ssh_decrypted(self):
        """Retorna a chave privada SSH descriptografada"""
        return self._decrypt(self.chave_privada_ssh) if self.chave_privada_ssh else None
    
    def get_senha_painel_decrypted(self):
        """Retorna a senha do painel descriptografada"""
        return self._decrypt(self.senha_painel) if self.senha_painel else None
    
    def get_senha_ftp_decrypted(self):
        """Retorna a senha FTP descriptografada"""
        return self._decrypt(self.senha_ftp) if self.senha_ftp else None
    
    def get_senha_mysql_decrypted(self):
        """Retorna a senha MySQL descriptografada"""
        return self._decrypt(self.senha_mysql) if self.senha_mysql else None
    
    def save(self, *args, **kwargs):
        """Override do save para criptografar campos sensíveis antes de salvar"""
        # Criptografar apenas se o valor não estiver já criptografado
        # (verificação: se começa com 'gAAAAAB' ou tem prefixo de aviso, já foi processado)
        campos_criptografar = [
            'senha', 'api_secret', 'auth_token', 'senha_ssh', 
            'chave_privada_ssh', 'senha_painel', 'senha_ftp', 'senha_mysql'
        ]
        
        for campo in campos_criptografar:
            valor = getattr(self, campo, None)
            if valor:
                # Não criptografar se já estiver criptografado ou processado
                if not (valor.startswith('gAAAAAB') or 
                        valor.startswith('[NÃO_CRIPTOGRAFADO]') or 
                        valor.startswith('[ERRO_CRIPTOGRAFIA]')):
                    setattr(self, campo, self._encrypt(valor))
        
        super().save(*args, **kwargs)


class Sistema(models.Model):
    """Model para cadastro de sistemas/aplicativos que utilizam os prompts"""
    
    nome = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nome do sistema/aplicativo (ex: 'MotoPro', 'VitrineZap', 'Évora')"
    )
    codigo = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código único do sistema (ex: 'motopro', 'vitrinezap', 'evora') - usado para identificação programática"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição do sistema e seu propósito"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Indica se o sistema está ativo e em uso"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre o sistema"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Sistema"
        verbose_name_plural = "Sistemas"
        ordering = ['nome']
        indexes = [
            models.Index(fields=['codigo', 'ativo']),
            models.Index(fields=['nome']),
        ]
    
    def __str__(self):
        status = "✓" if self.ativo else "✗"
        return f"{status} {self.nome} ({self.codigo})"


class PromptTemplate(models.Model):
    """Model para armazenar templates de prompts usados pelos serviços de IA"""
    
    TIPO_PROMPT_CHOICES = [
        ('analise_imagem_produto', 'Análise de Imagem de Produto'),
        ('extracao_json', 'Extração de JSON'),
        ('classificacao_categoria', 'Classificação de Categoria'),
        ('processamento_texto', 'Processamento de Texto'),
        ('traducao', 'Tradução'),
        ('resumo', 'Resumo'),
        ('outro', 'Outro'),
    ]
    
    sistema = models.ForeignKey(
        'Sistema',
        on_delete=models.CASCADE,
        related_name='prompts',
        null=True,
        blank=True,
        help_text="Sistema/aplicativo ao qual este prompt pertence"
    )
    
    nome = models.CharField(
        max_length=200,
        help_text="Nome identificador do prompt (ex: 'analise_produto_v1')"
    )
    descricao = models.TextField(
        blank=True,
        null=True,
        help_text="Descrição do que este prompt faz e quando deve ser usado"
    )
    tipo_prompt = models.CharField(
        max_length=50,
        choices=TIPO_PROMPT_CHOICES,
        default='outro',
        help_text="Tipo/categoria do prompt"
    )
    prompt_text = models.TextField(
        help_text="Texto completo do prompt que será enviado para a IA"
    )
    versao = models.CharField(
        max_length=20,
        default='1.0',
        help_text="Versão do prompt (ex: '1.0', '1.1', '2.0')"
    )
    ativo = models.BooleanField(
        default=True,
        help_text="Indica se este prompt está ativo e pode ser usado pelos serviços"
    )
    eh_padrao = models.BooleanField(
        default=False,
        help_text="Indica se este é o prompt padrão para o tipo. Apenas um prompt por tipo pode ser padrão."
    )
    parametros = models.JSONField(
        default=dict,
        blank=True,
        help_text="Parâmetros/configurações adicionais em formato JSON (ex: temperatura, max_tokens, etc)"
    )
    exemplos = models.TextField(
        blank=True,
        null=True,
        help_text="Exemplos de uso ou outputs esperados"
    )
    observacoes = models.TextField(
        blank=True,
        null=True,
        help_text="Observações sobre o prompt, mudanças recentes, testes realizados, etc"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Template de Prompt"
        verbose_name_plural = "Templates de Prompts"
        ordering = ['sistema', 'tipo_prompt', '-eh_padrao', '-versao', 'nome']
        unique_together = [['sistema', 'nome']]  # Nome único por sistema
        indexes = [
            models.Index(fields=['sistema', 'tipo_prompt', 'ativo', 'eh_padrao']),
            models.Index(fields=['sistema', 'nome']),
            models.Index(fields=['tipo_prompt', 'ativo', 'eh_padrao']),
        ]
    
    def __str__(self):
        status = "✓" if self.ativo else "✗"
        padrao = " [PADRÃO]" if self.eh_padrao else ""
        sistema_nome = self.sistema.nome if self.sistema else "Sem sistema"
        return f"{status} [{sistema_nome}] {self.nome} v{self.versao} ({self.get_tipo_prompt_display()}){padrao}"
    
    def save(self, *args, **kwargs):
        """Override do save para garantir que apenas um prompt seja padrão por tipo e sistema"""
        if self.eh_padrao:
            # Desativar outros prompts padrão do mesmo tipo e sistema
            PromptTemplate.objects.filter(
                sistema=self.sistema,
                tipo_prompt=self.tipo_prompt,
                eh_padrao=True
            ).exclude(pk=self.pk if self.pk else None).update(eh_padrao=False)
        super().save(*args, **kwargs)
    
    @classmethod
    def get_prompt_ativo(cls, tipo_prompt, sistema=None, nome=None):
        """
        Retorna o prompt ativo para um tipo específico e sistema
        
        Args:
            tipo_prompt: Tipo do prompt a buscar
            sistema: Sistema/aplicativo (pode ser objeto Sistema, código do sistema, ou None)
                     Se None, busca prompts sem sistema associado (legado)
            nome: Nome específico do prompt (opcional). Se não fornecido, retorna o padrão.
            
        Returns:
            PromptTemplate ou None
        """
        # Resolver sistema se fornecido como string (código) ou objeto
        sistema_obj = None
        if sistema:
            if isinstance(sistema, str):
                try:
                    sistema_obj = Sistema.objects.get(codigo=sistema, ativo=True)
                except Sistema.DoesNotExist:
                    logger.warning(f"Sistema com código '{sistema}' não encontrado ou inativo")
                    return None
            elif isinstance(sistema, Sistema):
                sistema_obj = sistema
            else:
                logger.warning(f"Tipo de sistema inválido: {type(sistema)}")
                return None
        
        if nome:
            try:
                if sistema_obj:
                    return cls.objects.get(sistema=sistema_obj, nome=nome, ativo=True)
                else:
                    # Buscar por nome sem sistema (pode ser legado)
                    return cls.objects.get(nome=nome, ativo=True, sistema__isnull=True)
            except cls.DoesNotExist:
                return None
        
        # Buscar o prompt padrão ativo do tipo e sistema
        query = cls.objects.filter(tipo_prompt=tipo_prompt, ativo=True, eh_padrao=True)
        if sistema_obj:
            query = query.filter(sistema=sistema_obj)
        else:
            # Se sistema não fornecido, buscar prompts sem sistema (legado)
            query = query.filter(sistema__isnull=True)
        
        try:
            return query.get()
        except cls.DoesNotExist:
            # Se não houver padrão, buscar qualquer prompt ativo do tipo e sistema
            query = cls.objects.filter(tipo_prompt=tipo_prompt, ativo=True)
            if sistema_obj:
                query = query.filter(sistema=sistema_obj)
            else:
                query = query.filter(sistema__isnull=True)
            return query.first()
    
    def get_prompt_text_com_parametros(self):
        """
        Retorna o texto do prompt com parâmetros aplicados se necessário
        Pode ser estendido para incluir formatação dinâmica
        """
        return self.prompt_text

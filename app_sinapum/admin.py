from django.contrib import admin
from .models import (
    Estabelecimento,
    Campanha,
    Shopper,
    ProdutoGenericoCatalogo,
    Produto,
    ProdutoViagem,
    CadastroMeta,
    ProdutoJSON,
    ServicoExterno,
    Sistema,
    PromptTemplate
)


@admin.register(Estabelecimento)
class EstabelecimentoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'endereco', 'latitude', 'longitude', 'criado_em']
    list_filter = ['criado_em']
    search_fields = ['nome', 'endereco']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(Campanha)
class CampanhaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_registro', 'criado_em']
    list_filter = ['data_registro', 'criado_em']
    search_fields = ['nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    date_hierarchy = 'data_registro'


@admin.register(Shopper)
class ShopperAdmin(admin.ModelAdmin):
    list_display = ['nome', 'pais', 'criado_em']
    list_filter = ['pais', 'criado_em']
    search_fields = ['nome', 'pais']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(ProdutoGenericoCatalogo)
class ProdutoGenericoCatalogoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marca', 'categoria', 'subcategoria', 'criado_em']
    list_filter = ['marca', 'categoria', 'subcategoria', 'criado_em']
    search_fields = ['nome', 'marca', 'categoria', 'subcategoria']
    readonly_fields = ['criado_em', 'atualizado_em']


class ProdutoViagemInline(admin.StackedInline):
    model = ProdutoViagem
    extra = 0
    fields = (
        'estabelecimento', 'campanha', 'shopper',
        'preco_compra_usd', 'preco_compra_brl',
        'margem_lucro_percentual',
        'preco_venda_usd', 'preco_venda_brl'
    )


class CadastroMetaInline(admin.StackedInline):
    model = CadastroMeta
    extra = 0
    fields = (
        'capturado_por', 'data_captura', 'fonte',
        'confianca_da_leitura', 'detalhes_rotulo'
    )


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'marca', 'categoria', 'subcategoria', 'codigo_barras', 'criado_em']
    list_filter = ['marca', 'categoria', 'subcategoria', 'tipo', 'criado_em']
    search_fields = ['nome', 'marca', 'codigo_barras', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
    inlines = [ProdutoViagemInline, CadastroMetaInline]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('produto_generico', 'nome', 'marca', 'descricao')
        }),
        ('Categorização', {
            'fields': ('categoria', 'subcategoria', 'familia_olfativa')
        }),
        ('Especificações', {
            'fields': ('volume_ml', 'tipo', 'codigo_barras')
        }),
        ('Imagens', {
            'fields': ('imagens',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProdutoViagem)
class ProdutoViagemAdmin(admin.ModelAdmin):
    list_display = ['produto', 'estabelecimento', 'preco_compra_brl', 'preco_venda_brl', 'margem_lucro_percentual', 'criado_em']
    list_filter = ['estabelecimento', 'campanha', 'shopper', 'criado_em']
    search_fields = ['produto__nome', 'produto__marca', 'estabelecimento__nome']
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Produto e Relacionamentos', {
            'fields': ('produto', 'estabelecimento', 'campanha', 'shopper')
        }),
        ('Preços de Compra', {
            'fields': ('preco_compra_usd', 'preco_compra_brl')
        }),
        ('Margem e Preços de Venda', {
            'fields': ('margem_lucro_percentual', 'preco_venda_usd', 'preco_venda_brl')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CadastroMeta)
class CadastroMetaAdmin(admin.ModelAdmin):
    list_display = ['produto', 'capturado_por', 'data_captura', 'confianca_da_leitura', 'fonte']
    list_filter = ['capturado_por', 'data_captura', 'confianca_da_leitura']
    search_fields = ['produto__nome', 'produto__marca', 'capturado_por', 'fonte']
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Produto', {
            'fields': ('produto',)
        }),
        ('Informações de Captura', {
            'fields': ('capturado_por', 'data_captura', 'fonte', 'confianca_da_leitura')
        }),
        ('Detalhes do Rótulo', {
            'fields': ('detalhes_rotulo',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProdutoJSON)
class ProdutoJSONAdmin(admin.ModelAdmin):
    list_display = ['nome_produto', 'marca', 'categoria', 'codigo_barras', 'criado_em']
    list_filter = ['marca', 'categoria', 'criado_em']
    search_fields = ['nome_produto', 'marca', 'codigo_barras', 'categoria']
    readonly_fields = ['criado_em', 'atualizado_em']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_produto', 'marca', 'categoria', 'codigo_barras', 'imagem_original')
        }),
        ('Dados JSON', {
            'fields': ('dados_json',),
            'description': 'Dados completos do produto no formato modelo.json'
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ServicoExterno)
class ServicoExternoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'tipo_servico', 'ambiente', 'ativo', 'ip_servidor', 'usuario', 'criado_em']
    list_filter = ['tipo_servico', 'ambiente', 'ativo', 'criado_em']
    search_fields = [
        'nome', 'tipo_servico', 'usuario', 'url_base', 'api_key', 
        'account_sid', 'ip_servidor', 'usuario_ssh', 'usuario_painel'
    ]
    readonly_fields = [
        'criado_em', 'atualizado_em', 
        'senha_readonly', 'api_secret_readonly', 'auth_token_readonly',
        'senha_ssh_readonly', 'chave_privada_ssh_readonly',
        'senha_painel_readonly', 'senha_ftp_readonly', 'senha_mysql_readonly'
    ]
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'tipo_servico', 'ambiente', 'ativo', 'url_base')
        }),
        ('Credenciais de Autenticação', {
            'fields': ('usuario', 'senha', 'senha_readonly'),
            'description': '⚠️ As senhas são criptografadas automaticamente ao salvar'
        }),
        ('API Keys e Tokens', {
            'fields': ('api_key', 'api_secret', 'api_secret_readonly', 'account_sid', 'auth_token', 'auth_token_readonly'),
            'description': '⚠️ API Secrets e Auth Tokens são criptografados automaticamente'
        }),
        ('Informações do Servidor VPS', {
            'fields': (
                'ip_servidor', 'sistema_operacional',
                'porta_ssh', 'usuario_ssh', 'senha_ssh', 'senha_ssh_readonly',
                'chave_privada_ssh', 'chave_privada_ssh_readonly'
            ),
            'description': 'Informações de acesso SSH ao servidor',
            'classes': ('collapse',)
        }),
        ('Painel de Controle', {
            'fields': (
                'url_painel_controle', 'usuario_painel', 
                'senha_painel', 'senha_painel_readonly'
            ),
            'description': 'Acesso ao painel de controle (cPanel, Plesk, etc)',
            'classes': ('collapse',)
        }),
        ('FTP', {
            'fields': (
                'porta_ftp', 'usuario_ftp', 
                'senha_ftp', 'senha_ftp_readonly'
            ),
            'description': 'Credenciais de acesso FTP',
            'classes': ('collapse',)
        }),
        ('Banco de Dados MySQL/MariaDB', {
            'fields': (
                'porta_mysql', 'usuario_mysql', 
                'senha_mysql', 'senha_mysql_readonly', 'nome_banco_dados'
            ),
            'description': 'Credenciais do banco de dados',
            'classes': ('collapse',)
        }),
        ('Credenciais Adicionais', {
            'fields': ('credenciais_adicionais',),
            'description': 'Campos adicionais em formato JSON (ex: {"project_id": "xxx", "database_url": "xxx", "domain": "xxx"})'
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def senha_readonly(self, obj):
        """Mostra indicação se a senha está definida (sem mostrar o valor)"""
        if obj and obj.senha:
            return "✓ Senha definida (criptografada)"
        return "✗ Nenhuma senha definida"
    senha_readonly.short_description = "Status da Senha"
    
    def api_secret_readonly(self, obj):
        """Mostra indicação se o API Secret está definido"""
        if obj and obj.api_secret:
            return "✓ API Secret definido (criptografado)"
        return "✗ Nenhum API Secret definido"
    api_secret_readonly.short_description = "Status do API Secret"
    
    def auth_token_readonly(self, obj):
        """Mostra indicação se o Auth Token está definido"""
        if obj and obj.auth_token:
            return "✓ Auth Token definido (criptografado)"
        return "✗ Nenhum Auth Token definido"
    auth_token_readonly.short_description = "Status do Auth Token"
    
    def senha_ssh_readonly(self, obj):
        """Mostra indicação se a senha SSH está definida"""
        if obj and obj.senha_ssh:
            return "✓ Senha SSH definida (criptografada)"
        return "✗ Nenhuma senha SSH definida"
    senha_ssh_readonly.short_description = "Status da Senha SSH"
    
    def chave_privada_ssh_readonly(self, obj):
        """Mostra indicação se a chave privada SSH está definida"""
        if obj and obj.chave_privada_ssh:
            return "✓ Chave privada SSH definida (criptografada)"
        return "✗ Nenhuma chave privada SSH definida"
    chave_privada_ssh_readonly.short_description = "Status da Chave Privada SSH"
    
    def senha_painel_readonly(self, obj):
        """Mostra indicação se a senha do painel está definida"""
        if obj and obj.senha_painel:
            return "✓ Senha do painel definida (criptografada)"
        return "✗ Nenhuma senha do painel definida"
    senha_painel_readonly.short_description = "Status da Senha do Painel"
    
    def senha_ftp_readonly(self, obj):
        """Mostra indicação se a senha FTP está definida"""
        if obj and obj.senha_ftp:
            return "✓ Senha FTP definida (criptografada)"
        return "✗ Nenhuma senha FTP definida"
    senha_ftp_readonly.short_description = "Status da Senha FTP"
    
    def senha_mysql_readonly(self, obj):
        """Mostra indicação se a senha MySQL está definida"""
        if obj and obj.senha_mysql:
            return "✓ Senha MySQL definida (criptografada)"
        return "✗ Nenhuma senha MySQL definida"
    senha_mysql_readonly.short_description = "Status da Senha MySQL"
    
    def get_readonly_fields(self, request, obj=None):
        """Campos readonly que dependem do objeto"""
        readonly = list(self.readonly_fields)
        return readonly


@admin.register(Sistema)
class SistemaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'codigo', 'ativo', 'criado_em', 'atualizado_em']
    list_filter = ['ativo', 'criado_em', 'atualizado_em']
    search_fields = ['nome', 'codigo', 'descricao']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'codigo', 'descricao')
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sistema', 'tipo_prompt', 'versao', 'ativo', 'eh_padrao', 'criado_em', 'atualizado_em']
    list_filter = ['sistema', 'tipo_prompt', 'ativo', 'eh_padrao', 'criado_em', 'atualizado_em']
    search_fields = ['nome', 'descricao', 'prompt_text', 'tipo_prompt', 'observacoes', 'sistema__nome', 'sistema__codigo']
    readonly_fields = ['criado_em', 'atualizado_em']
    
    fieldsets = (
        ('Sistema e Identificação', {
            'fields': ('sistema', 'nome', 'tipo_prompt', 'descricao', 'versao'),
            'description': '⚠️ O sistema identifica qual aplicativo usa este prompt. O nome do prompt deve ser único dentro do mesmo sistema.'
        }),
        ('Status e Configuração', {
            'fields': ('ativo', 'eh_padrao'),
            'description': '⚠️ Apenas um prompt por tipo e sistema pode ser marcado como padrão. Ao marcar este como padrão, os outros do mesmo tipo e sistema serão desmarcados automaticamente.'
        }),
        ('Prompt', {
            'fields': ('prompt_text',),
            'description': 'Texto completo do prompt que será enviado para a IA'
        }),
        ('Parâmetros e Configurações', {
            'fields': ('parametros',),
            'description': 'Parâmetros adicionais em formato JSON (ex: {"temperature": 0.3, "max_tokens": 4000})',
            'classes': ('collapse',)
        }),
        ('Documentação', {
            'fields': ('exemplos', 'observacoes'),
            'description': 'Exemplos de uso e observações sobre o prompt',
            'classes': ('collapse',)
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Otimizar queries com select_related se necessário"""
        qs = super().get_queryset(request)
        return qs
    
    def save_model(self, request, obj, form, change):
        """Override para garantir lógica de prompt padrão"""
        super().save_model(request, obj, form, change)

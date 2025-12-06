from django.contrib import admin
from .models import (
    Estabelecimento,
    Campanha,
    Shopper,
    ProdutoGenericoCatalogo,
    Produto,
    ProdutoViagem,
    CadastroMeta,
    ProdutoJSON
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

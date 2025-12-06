# Modelo de Produtos Django - Baseado em modelo.json

Este documento descreve a estrutura dos models Django criados baseados no arquivo `modelo.json`.

## Estrutura dos Models

### 1. Estabelecimento
Representa o estabelecimento onde o produto foi comprado.

**Campos:**
- `nome`: Nome do estabelecimento
- `endereco`: Endereço completo (opcional)
- `latitude`: Latitude geográfica (opcional)
- `longitude`: Longitude geográfica (opcional)
- `observacao`: Observações sobre o estabelecimento

**Relacionamentos:**
- Relacionado com `ProdutoViagem` (muitos produtos podem ser comprados no mesmo estabelecimento)

---

### 2. Campanha
Representa uma campanha relacionada à viagem de compras.

**Campos:**
- `nome`: Nome da campanha
- `data_registro`: Data de registro da campanha

**Relacionamentos:**
- Relacionado com `ProdutoViagem` (muitos produtos podem estar na mesma campanha)

---

### 3. Shopper
Representa o shopper responsável pela compra.

**Campos:**
- `nome`: Nome do shopper
- `pais`: País de origem do shopper

**Relacionamentos:**
- Relacionado com `ProdutoViagem` (um shopper pode comprar muitos produtos)

---

### 4. ProdutoGenericoCatalogo
Representa um produto genérico do catálogo (sem especificações de volume/tipo).

**Campos:**
- `nome`: Nome do produto genérico
- `marca`: Marca do produto
- `categoria`: Categoria principal
- `subcategoria`: Subcategoria
- `variantes`: Lista JSON com variantes (ex: `["50ml", "Parfum"]`)

**Relacionamentos:**
- Relacionado com `Produto` (um produto genérico pode ter muitas versões específicas)

**Constraint única:**
- Combinação única de `nome`, `marca`, `categoria` e `subcategoria`

---

### 5. Produto
Representa um produto específico com todas as informações detalhadas.

**Campos:**
- `produto_generico`: Referência ao produto genérico (opcional)
- `nome`: Nome completo do produto específico
- `marca`: Marca do produto
- `descricao`: Descrição detalhada
- `categoria`: Categoria principal
- `subcategoria`: Subcategoria
- `familia_olfativa`: Família olfativa (opcional, para perfumes)
- `volume_ml`: Volume em mililitros (opcional)
- `tipo`: Tipo do produto (ex: "Parfum")
- `codigo_barras`: Código de barras (único, opcional)
- `imagens`: Lista JSON com nomes dos arquivos de imagens

**Relacionamentos:**
- `OneToOne` com `ProdutoViagem` (informações financeiras)
- `OneToOne` com `CadastroMeta` (metadados do cadastro)

---

### 6. ProdutoViagem
Representa informações financeiras e de viagem relacionadas ao produto.

**Campos:**
- `produto`: Referência ao produto (OneToOne)
- `estabelecimento`: Estabelecimento onde foi comprado (opcional)
- `campanha`: Campanha relacionada (opcional)
- `shopper`: Shopper responsável (opcional)
- `preco_compra_usd`: Preço de compra em USD
- `preco_compra_brl`: Preço de compra em BRL
- `margem_lucro_percentual`: Margem de lucro em percentual
- `preco_venda_usd`: Preço de venda em USD
- `preco_venda_brl`: Preço de venda em BRL

**Métodos:**
- `calcular_preco_venda_brl()`: Calcula preço de venda em BRL baseado no preço de compra e margem
- `calcular_preco_venda_usd()`: Calcula preço de venda em USD baseado no preço de compra e margem

---

### 7. CadastroMeta
Representa metadados sobre o cadastro do produto (fonte, IA, confiança, etc).

**Campos:**
- `produto`: Referência ao produto (OneToOne)
- `capturado_por`: Sistema/IA que capturou os dados
- `data_captura`: Data/hora da captura
- `fonte`: Fonte dos dados (ex: "Fotos tiradas na loja")
- `confianca_da_leitura`: Confiança da leitura (0.0 a 1.0)
- `detalhes_rotulo`: Dicionário JSON com detalhes do rótulo (frase, origem, duração, etc)

---

## Como Criar as Migrações

Para criar e aplicar as migrações dos models:

```bash
# 1. Navegue até o diretório do projeto Django
cd /root/SinapUm

# 2. Ative o ambiente virtual (se houver)
source venv/bin/activate  # ou o caminho do seu venv

# 3. Crie as migrações
python manage.py makemigrations app_sinapum

# 4. Aplique as migrações ao banco de dados
python manage.py migrate

# 5. (Opcional) Crie um superusuário para acessar o admin
python manage.py createsuperuser
```

## Como Usar no Admin do Django

Os models estão registrados no admin Django com interfaces personalizadas:

1. **Estabelecimento**: Listagem com filtros por data e busca por nome/endereço
2. **Campanha**: Listagem com filtros por data e hierarquia de datas
3. **Shopper**: Listagem com filtros por país e busca por nome
4. **ProdutoGenericoCatalogo**: Listagem com filtros por marca, categoria e subcategoria
5. **Produto**: Interface completa com inlines para ProdutoViagem e CadastroMeta
6. **ProdutoViagem**: Listagem com informações financeiras e relacionamentos
7. **CadastroMeta**: Listagem com informações de captura e confiança

## Exemplo de Uso Programático

```python
from app_sinapum.models import (
    Estabelecimento, Campanha, Shopper,
    ProdutoGenericoCatalogo, Produto,
    ProdutoViagem, CadastroMeta
)

# Criar um estabelecimento
estabelecimento = Estabelecimento.objects.create(
    nome="Mega",
    latitude=-25.5095,
    longitude=-54.6115,
    observacao="Loja Mega (duty free / importados) em Ciudad del Este."
)

# Criar uma campanha
campanha = Campanha.objects.create(
    nome="Viagem Shopper – Mega Perfumes",
    data_registro="2025-11-22T00:00:00Z"
)

# Criar um shopper
shopper = Shopper.objects.create(
    nome="Shopper responsável",
    pais="Paraguai"
)

# Criar produto genérico
produto_generico = ProdutoGenericoCatalogo.objects.create(
    nome="1 Million Royal",
    marca="Paco Rabanne",
    categoria="Perfumaria",
    subcategoria="Perfume Masculino",
    variantes=["50ml", "Parfum"]
)

# Criar produto específico
produto = Produto.objects.create(
    produto_generico=produto_generico,
    nome="1 Million Royal 50ml",
    marca="Paco Rabanne",
    descricao="Perfume masculino 1 Million Royal, Paco Rabanne, 50 ml, Parfum Natural Spray.",
    categoria="Perfumaria",
    subcategoria="Perfume Masculino",
    volume_ml=50,
    tipo="Parfum",
    codigo_barras="3470498996753",
    imagens=[
        "1million_royal_frente.jpg",
        "1million_royal_verso.jpg",
        "1million_royal_preco.jpg"
    ]
)

# Criar produto viagem
produto_viagem = ProdutoViagem.objects.create(
    produto=produto,
    estabelecimento=estabelecimento,
    campanha=campanha,
    shopper=shopper,
    preco_compra_usd=55.0,
    preco_compra_brl=308.0,
    margem_lucro_percentual=100,
    preco_venda_usd=110.0,
    preco_venda_brl=616.0
)

# Criar cadastro meta
cadastro_meta = CadastroMeta.objects.create(
    produto=produto,
    capturado_por="VitrineZap (IA Évora)",
    data_captura="2025-11-22T00:00:00Z",
    fonte="Fotos tiradas na loja Mega",
    confianca_da_leitura=0.97,
    detalhes_rotulo={
        "frase": "conscious & vegan formula",
        "origem": "Made in France",
        "duracao": "very long-lasting"
    }
)
```

## Estrutura de Dados JSON

O modelo JSON original está mapeado da seguinte forma:

- `produto` → `Produto` model
- `produto_generico_catalogo` → `ProdutoGenericoCatalogo` model
- `produto_viagem` → `ProdutoViagem` model
- `estabelecimento` → `Estabelecimento` model
- `campanha` → `Campanha` model
- `shopper` → `Shopper` model
- `cadastro_meta` → `CadastroMeta` model


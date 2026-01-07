# AUDITORIA PASSIVA - VitrineZap vs Meu Catálogo Digital

**Data:** 2024
**Objetivo:** Mapear funcionalidades existentes antes de implementar melhorias do MCD

## 1. CATÁLOGO E PRODUTOS

### ✅ JÁ EXISTE
- **Modelo Produto** (`app_marketplace.models.Produto`): Produto básico com nome, descrição, preço, categoria, imagem
- **Modelo ProdutoJSON** (`app_marketplace.models.ProdutoJSON`): Produto em formato JSON flexível
- **Modelo WhatsappProduct** (`app_marketplace.models.WhatsappProduct`): Produto vinculado a grupos WhatsApp
- **Modelo Catalogo** (`app_marketplace.models.Catalogo`): Catálogos de produtos
- **MCP Tool catalog.search**: Busca no catálogo via MCP
- **EstoqueItem**: Gestão de estoque por agente (mas não por variação de produto)

### ⚠️ EXISTE PARCIALMENTE
- **Imagens**: Suporte a `image_urls` (JSONField) em WhatsappProduct, mas não em Produto base
- **Estoque**: Existe EstoqueItem, mas não suporta variações (tamanho, cor, etc.)

### ❌ NÃO EXISTE
- **Vídeos**: Nenhum suporte a video_urls em produtos
- **Variações de Produto**: Não há modelo para tamanho, cor, material, etc.
- **Estoque por Variação**: EstoqueItem não diferencia variações

## 2. MÍDIA

### ✅ JÁ EXISTE
- Suporte a vídeo no Evento Canônico (schemas_v1.py)
- Suporte a vídeo em mensagens WhatsApp (parsers, normalizers)
- Campo `video_url` em alguns modelos de conteúdo (PostConteudo)

### ❌ NÃO EXISTE
- **Vídeos em Produtos**: Produto/WhatsappProduct não suportam video_urls
- **Generators de Vídeo**: Não existe generators/video.py

## 3. MARKETING

### ✅ JÁ EXISTE
- **CupomDesconto** (`app_marketplace.models.CupomDesconto`): Modelo básico de cupom
- Cupons vinculados a Pedidos

### ⚠️ EXISTE PARCIALMENTE
- Cupons existem, mas não há:
  - Associação a Shopper específico
  - Associação a Produto específico
  - Associação a Campanha
  - Validação no checkout assistido pela IA

### ❌ NÃO EXISTE
- **Rastreamento**: Nenhum suporte a meta_pixel_id ou google_analytics_id
- **Eventos de Marketing**: product_view, add_to_cart, checkout_intent não são disparados
- **Serviço de Marketing**: Não existe marketing_tools_service

## 4. ACESSO AO CATÁLOGO

### ✅ JÁ EXISTE
- **app_console**: Console administrativo para Shoppers
- Views básicas de dashboard e conversas

### ❌ NÃO EXISTE
- Configuração de subdomínio/domínio próprio
- Página pública de catálogo (somente leitura)
- Link direto para catálogo do Shopper

## 5. RESPOSTA AUTOMÁTICA

### ✅ JÁ EXISTE
- Campo `auto_reply_sent` em alguns modelos de mensagem WhatsApp
- Suporte a auto_reply em Chatwoot (mas não no VitrineZap)

### ❌ NÃO EXISTE
- Detecção de mensagens fora do horário de atendimento
- Envio automático de mensagem contextual com link do catálogo
- Configuração de horário de atendimento por Shopper

## DECISÕES ARQUITETURAIS

1. **NÃO alterar modelos existentes** - apenas estender
2. **Manter retrocompatibilidade** - todos os campos novos são opcionais
3. **MCP como única porta** - todas as novas funcionalidades expostas via MCP
4. **IA sempre sugere, Shopper sempre confirma** - princípio inviolável


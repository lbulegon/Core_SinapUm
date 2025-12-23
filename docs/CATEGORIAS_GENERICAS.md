# Categorias Genéricas para E-commerce

## 🎯 Objetivo

O sistema Openmind Evora usa categorias **GENÉRICAS e AMPLAS** para permitir a comercialização de **qualquer tipo de produto** sem restrições.

## 📋 Lista de Categorias Genéricas

### 1. **Alimentos e Bebidas**
- Comida, bebidas, suplementos alimentares
- Exemplos: Arroz, Refrigerante, Água, Biscoitos, etc.

### 2. **Limpeza e Higiene**
- Produtos de limpeza doméstica e higiene pessoal
- Exemplos: Detergente, Sabão, Papel Higiênico, etc.

### 3. **Cosméticos e Perfumaria**
- Perfumes, maquiagem, produtos de beleza
- Exemplos: Perfume, Batom, Shampoo, etc.

### 4. **Eletrônicos**
- Aparelhos e acessórios eletrônicos
- Exemplos: Celular, Fones, Carregadores, etc.

### 5. **Casa e Jardim**
- Utensílios domésticos, decoração, jardinagem
- Exemplos: Panelas, Vasos, Lâmpadas, etc.

### 6. **Automotivo**
- Peças, acessórios e produtos automotivos
- Exemplos: Pneus, Óleo, Bateria, etc.

### 7. **Esportes e Lazer**
- Equipamentos e acessórios esportivos
- Exemplos: Bola, Tênis, Bicicleta, etc.

### 8. **Roupas e Acessórios**
- Vestuário e acessórios pessoais
- Exemplos: Camisa, Bolsa, Relógio, etc.

### 9. **Ferramentas e Equipamentos**
- Ferramentas, máquinas, equipamentos profissionais
- Exemplos: Chave de Fenda, Furadeira, etc.

### 10. **Químicos e Industriais**
- Produtos químicos, materiais industriais, gases
- Exemplos: Gás Refrigerante, Resina, Adesivo Industrial, etc.

### 11. **Saúde e Farmacêuticos**
- Medicamentos, produtos médicos, suplementos
- Exemplos: Remédios, Termômetro, etc.

### 12. **Refrigerantes e Gases**
- Gases refrigerantes, industriais, especiais
- Exemplos: R-410A, Gás de Cozinha, Gás Industrial, etc.

### 13. **Outros**
- Use apenas se o produto não se encaixar em nenhuma categoria acima
- Categoria de fallback para produtos incomuns

---

## 📝 Diretrizes de Uso

### Para Categorias (campo `categoria`):
- ✅ Use APENAS as categorias da lista acima
- ✅ Escolha a categoria mais genérica que ainda seja apropriada
- ❌ NÃO crie novas categorias
- ❌ NÃO use categorias muito específicas

### Para Subcategorias (campo `subcategoria`):
- ✅ Use nível intermediário de detalhe
- ✅ Seja específico o suficiente para ser útil
- ❌ NÃO seja excessivamente detalhado
- ✅ Exemplos bons: "Gás Refrigerante", "Sabão em Pó", "Perfume"
- ❌ Exemplos ruins: "Gás Refrigerante R-410A para Ar-Condicionado Split de 12.000 BTUs" (muito específico)

---

## 🔄 Exemplos de Classificação

### Exemplo 1: RLX 410 (Gás Refrigerante)
- **Categoria**: `Refrigerantes e Gases` ✅
- **Subcategoria**: `Gás Refrigerante` ✅
- ❌ **ERRADO**: Categoria "Limpeza" ou "Produto de Limpeza"

### Exemplo 2: Detergente Ypê
- **Categoria**: `Limpeza e Higiene` ✅
- **Subcategoria**: `Detergente` ✅

### Exemplo 3: Perfume Chanel
- **Categoria**: `Cosméticos e Perfumaria` ✅
- **Subcategoria**: `Perfume` ✅

### Exemplo 4: Smartphone Samsung
- **Categoria**: `Eletrônicos` ✅
- **Subcategoria**: `Smartphone` ou `Celular` ✅

### Exemplo 5: Bicicleta Caloi
- **Categoria**: `Esportes e Lazer` ✅
- **Subcategoria**: `Bicicleta` ✅

---

## ⚙️ Configuração no Sistema

O prompt do sistema foi ajustado para:
1. Listar as categorias genéricas disponíveis
2. Instruir a IA a usar APENAS essas categorias
3. Não criar novas categorias
4. Escolher a categoria mais apropriada e genérica

---

## 📊 Benefícios

✅ **Flexibilidade**: Permite comercializar qualquer tipo de produto
✅ **Organização**: Categorias claras e consistentes
✅ **Escalabilidade**: Fácil de adicionar novos produtos
✅ **Navegação**: Clientes encontram produtos facilmente
✅ **Manutenção**: Sistema simples e fácil de manter

---

**Última atualização**: 06/12/2025
**Status**: Ativo e em produção


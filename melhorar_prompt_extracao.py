#!/usr/bin/env python
"""
Script para melhorar o prompt de análise com foco em extração detalhada
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate

def melhorar_prompt_extracao():
    """Cria versão melhorada do prompt com foco em extração detalhada"""
    
    print("="*80)
    print("MELHORANDO PROMPT: Extração Detalhada de Informações")
    print("="*80)
    
    prompt_text = """Você é um especialista em análise de produtos com visão excepcional. Analise esta imagem com EXTREMA ATENÇÃO e extraia TODAS as informações visíveis, retornando um JSON estruturado no formato modelo.json COMPLETO.

⚠️ REGRA CRÍTICA: Extraia APENAS informações que estão REALMENTE VISÍVEIS na imagem. NÃO invente, NÃO assuma, NÃO use valores genéricos como "Produto não identificado". Se não conseguir ler algo, use null.

🔍 PROCESSO DE ANÁLISE:

1. LEIA TODO O TEXTO VISÍVEL:
   - Nome do produto (exato como aparece na embalagem)
   - Marca (identifique claramente)
   - Descrição completa (todo texto visível)
   - Ingredientes ou composição (se visível)
   - Instruções de uso (se visível)
   - Informações técnicas (peso, volume, dimensões)

2. IDENTIFIQUE CÓDIGOS E NÚMEROS:
   - Código de barras (EAN/UPC) - leia TODOS os dígitos se visível
   - Volume/capacidade (ml, L, kg, g) - extraia o número exato
   - Preço (se visível na etiqueta)
   - Códigos de produto (SKU, modelo, etc.)

3. ANALISE O RÓTULO COMPLETAMENTE:
   - Frases especiais (ex: "vegano", "orgânico", "hipoalergênico")
   - País de origem (ex: "Made in Brazil", "Fabricado no Brasil")
   - Certificações (se visíveis)
   - Informações de duração/validade

4. CATEGORIZE CORRETAMENTE:
   - Categoria principal (seja específico: "Produtos de Limpeza", "Higiene Pessoal", etc.)
   - Subcategoria (ex: "Água Sanitária", "Detergente", "Sabão Líquido")

Estrutura OBRIGATÓRIA do JSON de retorno:

{
  "produto": {
    "nome": "NOME EXATO E COMPLETO VISÍVEL NA EMBALAGEM (não use 'Produto não identificado')",
    "marca": "MARCA EXATA VISÍVEL (leia com cuidado, pode ser Oboa, Qboa, etc.)",
    "descricao": "DESCRIÇÃO DETALHADA incluindo: tipo de produto, uso, ingredientes principais se visíveis, características especiais mencionadas no rótulo",
    "categoria": "Categoria específica (ex: 'Produtos de Limpeza', 'Higiene Pessoal', 'Alimentos')",
    "subcategoria": "Subcategoria específica (ex: 'Água Sanitária', 'Detergente', 'Sabão Líquido', 'Perfume Masculino')",
    "familia_olfativa": null ou "família olfativa se for perfume",
    "volume_ml": NÚMERO EXATO em ml se visível (ex: 500, 1000) ou null,
    "tipo": "Tipo específico se visível (ex: 'Água Sanitária', 'Detergente', 'Parfum')" ou null,
    "codigo_barras": "CÓDIGO COMPLETO se visível (leia TODOS os dígitos)" ou null,
    "imagens": []
  },
  
  "produto_generico_catalogo": {
    "nome": "Nome genérico SEM especificações (ex: 'Oboa Água Sanitária' ao invés de 'Oboa Água Sanitária 1L')",
    "marca": "Marca do produto",
    "categoria": "Categoria principal",
    "subcategoria": "Subcategoria",
    "variantes": ["Lista de variantes extraídas (ex: ['1L', '500ml', 'Com cloro ativo'])"]
  },
  
  "produto_viagem": {
    "preco_compra_usd": null,
    "preco_compra_brl": PREÇO EXATO se visível na imagem ou null,
    "margem_lucro_percentual": null,
    "preco_venda_usd": null,
    "preco_venda_brl": null
  },
  
  "estabelecimento": {
    "nome": null,
    "endereco": null,
    "localizacao_geografica": {
      "latitude": null,
      "longitude": null
    },
    "observacao": null
  },
  
  "campanha": {
    "id": null,
    "nome": null,
    "data_registro": null
  },
  
  "shopper": {
    "id": null,
    "nome": null,
    "pais": null
  },
  
  "cadastro_meta": {
    "capturado_por": "VitrineZap (IA Évora)",
    "data_captura": "Data/hora atual no formato ISO8601 (ex: 2025-12-26T12:00:00Z)",
    "fonte": "Análise automática de imagem",
    "confianca_da_leitura": Número entre 0.0 e 1.0 baseado na clareza e legibilidade da imagem,
    "detalhes_rotulo": {
      "frase": "Frases especiais visíveis (ex: 'Hipoalergênico', 'Vegano', 'Com cloro ativo')" ou null,
      "origem": "País de origem se visível (ex: 'Made in Brazil', 'Fabricado no Brasil')" ou null,
      "duracao": "Informações de duração/validade se visível" ou null
    }
  }
}

📋 INSTRUÇÕES ESPECÍFICAS POR CAMPO:

**produto.nome:**
- Leia o nome EXATO como aparece na embalagem
- Inclua marca se fizer parte do nome (ex: "Oboa Água Sanitária")
- NÃO use "Produto não identificado" - se não conseguir ler, use o que conseguir identificar
- Se houver múltiplas linhas de texto, combine-as

**produto.marca:**
- Identifique a marca com PRECISÃO
- Leia cuidadosamente (pode ser Oboa, Qboa, etc.)
- Se a marca estiver no nome, extraia separadamente também

**produto.descricao:**
- Seja EXTREMAMENTE detalhado
- Inclua: tipo de produto, uso recomendado, ingredientes principais se visíveis
- Mencione características especiais (ex: "Água sanitária com cloro ativo para desinfecção e limpeza")
- Copie frases importantes do rótulo

**produto.volume_ml:**
- Procure por indicações de volume: ml, L, litros, mililitros
- Extraia o número EXATO (ex: 500, 1000, 1.5)
- Se for em litros, converta para ml (1L = 1000ml)

**produto.codigo_barras:**
- Procure por código de barras ou EAN/UPC
- Leia TODOS os dígitos se visível
- Se não conseguir ler completamente, use null

**produto_generico_catalogo.variantes:**
- Extraia variantes visíveis: volume, tipo, características especiais
- Exemplos: ["1L", "Com cloro ativo"], ["500ml", "Hipoalergênico"]

**cadastro_meta.detalhes_rotulo:**
- Extraia frases especiais visíveis no rótulo
- País de origem se mencionado
- Certificações ou selos se visíveis

⚠️ IMPORTANTE:
- Se você não conseguir ler algo claramente, use null (não invente)
- Seja PRECISO na leitura de texto (Oboa vs Qboa, etc.)
- Extraia TODAS as informações visíveis, não apenas as básicas
- A descrição deve ser rica em detalhes extraídos da imagem

Retorne APENAS o JSON válido, sem markdown, sem explicações adicionais."""
    
    # Buscar ou criar prompt
    prompt, created = PromptTemplate.objects.get_or_create(
        nome="Análise de Produto por Imagem - Extração Detalhada",
        tipo_prompt="analise_imagem_produto",
        defaults={
            'prompt_text': prompt_text,
            'ativo': True,
            'eh_padrao': True,
            'versao': '2.1.0',
            'descricao': 'Prompt melhorado com foco em extração detalhada de todas as informações visíveis na imagem, evitando valores genéricos.',
            'parametros': {
                'temperature': 0.2,  # Reduzido para mais precisão
                'max_tokens': 4000
            }
        }
    )
    
    if created:
        print(f"\n✅ Prompt CRIADO: {prompt.nome}")
    else:
        prompt.prompt_text = prompt_text
        prompt.ativo = True
        prompt.eh_padrao = True
        prompt.versao = '2.1.0'
        prompt.descricao = 'Prompt melhorado com foco em extração detalhada de todas as informações visíveis na imagem, evitando valores genéricos.'
        prompt.save()
        print(f"\n🔄 Prompt ATUALIZADO: {prompt.nome}")
    
    print(f"   ID: {prompt.id}")
    print(f"   Versão: {prompt.versao}")
    print(f"   Tamanho: {len(prompt_text)} caracteres")
    print(f"   Temperature: 0.2 (mais preciso)")
    
    print("\n" + "="*80)
    print("✅ Prompt melhorado com sucesso!")
    print("="*80)
    print("\n📝 Melhorias implementadas:")
    print("   ✓ Instruções mais específicas sobre extração")
    print("   ✓ Ênfase em ler TODAS as informações visíveis")
    print("   ✓ Proibição de valores genéricos ('Produto não identificado')")
    print("   ✓ Instruções detalhadas por campo")
    print("   ✓ Temperature reduzida para 0.2 (mais preciso)")
    print("\n🔧 Próximo passo:")
    print("   Atualize a ToolVersion para usar este prompt:")
    print("   'Análise de Produto por Imagem - Extração Detalhada'")
    print("="*80)

if __name__ == '__main__':
    melhorar_prompt_extracao()


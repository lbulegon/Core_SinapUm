#!/usr/bin/env python
"""
Script para criar versão v3 do prompt com foco máximo em precisão
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate

def criar_prompt_v3():
    """Cria versão v3 do prompt com máxima precisão"""
    
    print("="*80)
    print("CRIANDO PROMPT v3: Máxima Precisão e Extração Completa")
    print("="*80)
    
    prompt_text = """Você é um especialista em análise de produtos com capacidade de leitura excepcional. Sua tarefa é analisar esta imagem com EXTREMA PRECISÃO e extrair TODAS as informações visíveis, retornando um JSON estruturado no formato modelo.json COMPLETO.

🚨 REGRAS CRÍTICAS (NÃO IGNORE):

1. NUNCA use "Produto não identificado" no nome. Se não conseguir ler o nome completo, use o que conseguir identificar (marca + tipo de produto).

2. LEIA TODO O TEXTO VISÍVEL na embalagem, incluindo:
   - Nome do produto (exato como aparece)
   - Marca (exata como aparece)
   - Tipo de produto (ex: "Lava Roupas em Pó", "Água Sanitária")
   - Peso/Volume (4KG, 1L, 500ml, etc.) - EXTRAIA O NÚMERO EXATO
   - Características especiais (MATIC, Perfume Intenso, Nova Fórmula, etc.)
   - Código de barras (se visível)

3. Para PESO (KG, g): Se houver peso visível (ex: 4KG), NÃO coloque em volume_ml. O campo volume_ml é apenas para líquidos. Para produtos em pó/sólidos com peso, deixe volume_ml como null mas extraia o peso na descrição.

4. Seja EXTREMAMENTE detalhado na descrição. Inclua:
   - Tipo completo do produto
   - Peso/volume visível
   - Características especiais mencionadas
   - Uso recomendado se visível
   - Qualquer informação técnica visível

Estrutura OBRIGATÓRIA do JSON:

{
  "produto": {
    "nome": "NOME EXATO E COMPLETO como aparece na embalagem (ex: 'GOTA limpa Lava Roupas em Pó', 'Oboa Água Sanitária'). NUNCA use 'Produto não identificado'",
    "marca": "MARCA EXATA como aparece (ex: 'GOTA limpa', 'Oboa')",
    "descricao": "DESCRIÇÃO COMPLETA E DETALHADA incluindo: tipo de produto completo, peso/volume visível (ex: '4KG', '1L'), características especiais (ex: 'MATIC', 'Perfume Intenso', 'Nova Fórmula'), uso recomendado, ingredientes principais se visíveis. Seja EXTREMAMENTE detalhado.",
    "categoria": "Categoria específica (ex: 'Produtos de Limpeza', 'Higiene Pessoal')",
    "subcategoria": "Subcategoria específica (ex: 'Detergente em Pó', 'Água Sanitária', 'Sabão Líquido')",
    "familia_olfativa": null,
    "volume_ml": NÚMERO em ml APENAS se for produto líquido com volume visível (ex: 500, 1000). Se for produto em pó/sólido com peso (KG/g), deixe null,
    "tipo": "Tipo específico se visível (ex: 'Lava Roupas em Pó', 'Água Sanitária', 'Detergente', 'MATIC')" ou null,
    "codigo_barras": "CÓDIGO COMPLETO se visível (leia TODOS os dígitos)" ou null,
    "imagens": []
  },
  
  "produto_generico_catalogo": {
    "nome": "Nome genérico SEM peso/volume (ex: 'GOTA limpa Lava Roupas em Pó' ao invés de 'GOTA limpa Lava Roupas em Pó 4KG')",
    "marca": "Marca do produto",
    "categoria": "Categoria principal",
    "subcategoria": "Subcategoria",
    "variantes": ["Lista de TODAS as variantes visíveis: peso (ex: '4KG'), tipo (ex: 'MATIC'), características (ex: 'Perfume Intenso', 'Nova Fórmula')"]
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
    "confianca_da_leitura": Número entre 0.0 e 1.0 baseado na clareza da imagem,
    "detalhes_rotulo": {
      "frase": "Frases especiais visíveis (ex: 'Perfume Intenso', 'Nova Fórmula', 'MATIC', 'Hipoalergênico')" ou null,
      "origem": "País de origem se visível (ex: 'Made in Brazil', 'Fabricado no Brasil')" ou null,
      "duracao": "Informações de duração/validade se visível" ou null
    }
  }
}

📋 INSTRUÇÕES DETALHADAS POR CAMPO:

**produto.nome:**
- Leia o nome EXATO como aparece na embalagem
- Inclua marca + tipo de produto (ex: "GOTA limpa Lava Roupas em Pó")
- NÃO inclua peso/volume no nome (ex: não use "GOTA limpa 4KG")
- NUNCA use "Produto não identificado" - se não conseguir ler tudo, use marca + tipo de produto

**produto.marca:**
- Identifique a marca com PRECISÃO
- Leia exatamente como aparece (ex: "GOTA limpa", não "Gota Limpa")

**produto.descricao:**
- Seja EXTREMAMENTE detalhado
- INCLUA: tipo completo, peso/volume visível, características especiais
- Exemplo bom: "GOTA limpa Lava Roupas em Pó. Detergente em pó para máquinas de lavar automáticas (MATIC). Peso: 4KG. Características: Perfume Intenso, Nova Fórmula com poder de limpeza. Indicado para lavagem de roupas brancas e coloridas."
- NÃO seja vago como "Gota Limpa. Lava Roupas em Pó"

**produto.subcategoria:**
- Seja específico (ex: "Detergente em Pó", "Água Sanitária", "Sabão Líquido")
- NÃO deixe vazio se conseguir identificar

**produto.volume_ml:**
- APENAS para produtos líquidos com volume visível (ml ou L)
- Se for produto em pó/sólido com peso (KG, g), deixe null
- Se houver volume, converta L para ml (1L = 1000ml)

**produto.tipo:**
- Extraia tipo específico se visível (ex: "Lava Roupas em Pó", "MATIC", "Água Sanitária")
- Pode ser o tipo de produto ou característica especial

**produto_generico_catalogo.variantes:**
- Extraia TODAS as variantes visíveis:
  - Peso: "4KG", "1KG", "500g"
  - Tipo: "MATIC", "Tradicional"
  - Características: "Perfume Intenso", "Nova Fórmula", "Hipoalergênico"
- Exemplo: ["4KG", "MATIC", "Perfume Intenso", "Nova Fórmula"]

**cadastro_meta.detalhes_rotulo.frase:**
- Extraia frases especiais visíveis
- Exemplos: "Perfume Intenso", "Nova Fórmula", "MATIC", "Poder de limpeza"

⚠️ CHECKLIST ANTES DE RETORNAR:

□ Nome não contém "Produto não identificado"
□ Descrição é detalhada e inclui peso/volume se visível
□ Variantes incluem peso e características especiais
□ Subcategoria está preenchida (não vazia)
□ Detalhes do rótulo incluem frases especiais se visíveis
□ Todas as informações visíveis foram extraídas

Retorne APENAS o JSON válido, sem markdown, sem explicações adicionais."""
    
    # Criar ou atualizar prompt
    prompt, created = PromptTemplate.objects.get_or_create(
        nome="Análise de Produto - Máxima Precisão v3",
        tipo_prompt="analise_imagem_produto",
        defaults={
            'prompt_text': prompt_text,
            'ativo': True,
            'eh_padrao': True,
            'versao': '3.0.0',
            'descricao': 'Prompt v3 com foco máximo em precisão: extração completa de nome, peso, características e todas informações visíveis. Proibição explícita de valores genéricos.',
            'parametros': {
                'temperature': 0.1,  # Ainda mais baixo para máxima precisão
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
        prompt.versao = '3.0.0'
        prompt.descricao = 'Prompt v3 com foco máximo em precisão: extração completa de nome, peso, características e todas informações visíveis. Proibição explícita de valores genéricos.'
        prompt.parametros = {
            'temperature': 0.1,
            'max_tokens': 4000
        }
        prompt.save()
        print(f"\n🔄 Prompt ATUALIZADO: {prompt.nome}")
    
    # Tornar global (sem sistema)
    prompt.sistema = None
    prompt.save()
    
    print(f"   ID: {prompt.id}")
    print(f"   Versão: {prompt.versao}")
    print(f"   Tamanho: {len(prompt_text)} caracteres")
    print(f"   Temperature: 0.1 (máxima precisão)")
    print(f"   Sistema: Global")
    
    print("\n" + "="*80)
    print("✅ Prompt v3 criado com sucesso!")
    print("="*80)
    print("\n📝 Melhorias principais:")
    print("   ✓ Proibição EXPLÍCITA de 'Produto não identificado'")
    print("   ✓ Instruções específicas para extrair peso (4KG, etc.)")
    print("   ✓ Checklist antes de retornar")
    print("   ✓ Temperature 0.1 (máxima precisão)")
    print("   ✓ Instruções detalhadas para cada campo")
    print("   ✓ Exemplos concretos de descrições boas vs ruins")
    print("\n🔧 Próximo passo:")
    print("   Atualize a ToolVersion para usar: 'Análise de Produto - Máxima Precisão v3'")
    print("="*80)

if __name__ == '__main__':
    criar_prompt_v3()


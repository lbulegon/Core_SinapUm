#!/usr/bin/env python
"""
Script para criar prompt v4 ultra específico e direto
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate

def criar_prompt_v4():
    """Cria versão v4 do prompt com instruções ultra específicas"""
    
    print("="*80)
    print("CRIANDO PROMPT v4: Ultra Específico e Direto")
    print("="*80)
    
    prompt_text = """Analise esta imagem de produto e extraia TODAS as informações visíveis. Retorne APENAS um JSON válido no formato especificado abaixo.

🚨 REGRAS ABSOLUTAS:

1. NOME DO PRODUTO:
   - Leia o nome EXATO como aparece na embalagem
   - NUNCA use "Produto não identificado"
   - Se não conseguir ler tudo, use: MARCA + TIPO DE PRODUTO
   - Exemplo: "GOTA limpa Lava Roupas em Pó" (não "Produto não identificado – Gota Limpa")

2. PESO/VOLUME:
   - PROCURE por números seguidos de: KG, g, L, ml, litros
   - Se encontrar "4KG", extraia "4KG" e mencione na descrição e variantes
   - Se encontrar "1L", extraia e converta para ml (1000ml)
   - NÃO deixe volume_ml como null se houver peso/volume visível

3. DESCRIÇÃO:
   - Seja EXTREMAMENTE detalhado
   - INCLUA: tipo completo, peso/volume, características especiais
   - Exemplo BOM: "GOTA limpa Lava Roupas em Pó. Detergente em pó para máquinas automáticas (MATIC). Peso: 4KG. Características: Perfume Intenso, Nova Fórmula com poder de limpeza."
   - Exemplo RUIM: "Gota Limpa. Lava Roupas em Pó" (muito vago)

4. VARIANTES:
   - Extraia TODAS: peso (4KG, 1KG), tipo (MATIC), características (Perfume Intenso, Nova Fórmula)
   - Exemplo: ["4KG", "MATIC", "Perfume Intenso", "Nova Fórmula"]

5. SUBCATEGORIA:
   - Seja específico: "Detergente em Pó", "Água Sanitária", "Sabão Líquido"
   - NÃO deixe vazio

6. DETALHES DO RÓTULO:
   - Extraia frases visíveis: "Perfume Intenso", "Nova Fórmula", "MATIC", etc.
   - Se houver país de origem, extraia

Retorne este JSON (substitua os valores pelos dados reais da imagem):

{
  "produto": {
    "nome": "NOME EXATO DA EMBALAGEM (ex: 'GOTA limpa Lava Roupas em Pó')",
    "marca": "MARCA EXATA (ex: 'GOTA limpa')",
    "descricao": "DESCRIÇÃO COMPLETA incluindo tipo, peso (ex: '4KG'), características (ex: 'MATIC', 'Perfume Intenso', 'Nova Fórmula')",
    "categoria": "Produtos de Limpeza",
    "subcategoria": "SUBCATEGORIA ESPECÍFICA (ex: 'Detergente em Pó', 'Água Sanitária')",
    "familia_olfativa": null,
    "volume_ml": NÚMERO se produto líquido ou null se sólido/pó,
    "tipo": "TIPO se visível (ex: 'Lava Roupas em Pó', 'MATIC')" ou null,
    "codigo_barras": "CÓDIGO se visível" ou null,
    "imagens": []
  },
  "produto_generico_catalogo": {
    "nome": "Nome sem peso (ex: 'GOTA limpa Lava Roupas em Pó')",
    "marca": "Marca",
    "categoria": "Categoria",
    "subcategoria": "Subcategoria",
    "variantes": ["PESO se visível (ex: '4KG')", "TIPO se visível (ex: 'MATIC')", "CARACTERÍSTICAS (ex: 'Perfume Intenso', 'Nova Fórmula')"]
  },
  "produto_viagem": {
    "preco_compra_usd": null,
    "preco_compra_brl": null,
    "margem_lucro_percentual": null,
    "preco_venda_usd": null,
    "preco_venda_brl": null
  },
  "estabelecimento": {
    "nome": null,
    "endereco": null,
    "localizacao_geografica": {"latitude": null, "longitude": null},
    "observacao": null
  },
  "campanha": {"id": null, "nome": null, "data_registro": null},
  "shopper": {"id": null, "nome": null, "pais": null},
  "cadastro_meta": {
    "capturado_por": "VitrineZap (IA Évora)",
    "data_captura": "Data atual ISO8601",
    "fonte": "Análise automática de imagem",
    "confianca_da_leitura": 0.95,
    "detalhes_rotulo": {
      "frase": "Frases visíveis (ex: 'Perfume Intenso', 'Nova Fórmula', 'MATIC')" ou null,
      "origem": "País se visível" ou null,
      "duracao": null
    }
  }
}

⚠️ ANTES DE RETORNAR, VERIFIQUE:
- Nome NÃO contém "Produto não identificado"?
- Descrição inclui peso e características?
- Variantes incluem peso e características?
- Subcategoria está preenchida?
- Detalhes do rótulo incluem frases visíveis?

Retorne APENAS o JSON, sem markdown, sem explicações."""
    
    # Criar ou atualizar prompt
    prompt, created = PromptTemplate.objects.get_or_create(
        nome="Análise de Produto - Ultra Específico v4",
        tipo_prompt="analise_imagem_produto",
        defaults={
            'prompt_text': prompt_text,
            'ativo': True,
            'eh_padrao': True,
            'versao': '4.0.0',
            'descricao': 'Prompt v4 ultra específico: instruções diretas com exemplos concretos. Foco máximo em extrair nome exato, peso, características e todas informações visíveis.',
            'parametros': {
                'temperature': 0.0,  # Zero para máxima precisão
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
        prompt.versao = '4.0.0'
        prompt.descricao = 'Prompt v4 ultra específico: instruções diretas com exemplos concretos. Foco máximo em extrair nome exato, peso, características e todas informações visíveis.'
        prompt.parametros = {
            'temperature': 0.0,
            'max_tokens': 4000
        }
        prompt.save()
        print(f"\n🔄 Prompt ATUALIZADO: {prompt.nome}")
    
    # Tornar global
    prompt.sistema = None
    prompt.save()
    
    print(f"   ID: {prompt.id}")
    print(f"   Versão: {prompt.versao}")
    print(f"   Tamanho: {len(prompt_text)} caracteres")
    print(f"   Temperature: 0.0 (máxima precisão - sem criatividade)")
    print(f"   Sistema: Global")
    
    print("\n" + "="*80)
    print("✅ Prompt v4 criado!")
    print("="*80)
    print("\n📝 Melhorias principais:")
    print("   ✓ Instruções mais diretas e específicas")
    print("   ✓ Exemplos concretos de BOM vs RUIM")
    print("   ✓ Checklist antes de retornar")
    print("   ✓ Temperature 0.0 (máxima precisão)")
    print("   ✓ Formato JSON de exemplo incluído")
    print("\n🔧 Próximo passo:")
    print("   Atualize para usar: 'Análise de Produto - Ultra Específico v4'")
    print("="*80)

if __name__ == '__main__':
    criar_prompt_v4()


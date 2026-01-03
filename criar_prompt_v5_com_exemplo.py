#!/usr/bin/env python
"""
Script para criar prompt v5 com exemplo concreto
"""
import os
import sys
import django

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate

def criar_prompt_v5():
    """Cria versão v5 do prompt com exemplo concreto"""
    
    print("="*80)
    print("CRIANDO PROMPT v5: Com Exemplo Concreto")
    print("="*80)
    
    prompt_text = """Analise esta imagem de produto e extraia TODAS as informações visíveis. Retorne APENAS um JSON válido.

🚨 REGRAS CRÍTICAS:

1. NOME: Leia o nome EXATO da embalagem. NUNCA use "Produto não identificado".
   - Se ver "GOTA limpa Lava Roupas em Pó", retorne exatamente isso
   - Se ver "Oboa Água Sanitária", retorne exatamente isso
   - NÃO invente, NÃO generalize

2. PESO/VOLUME: PROCURE por números com unidades (4KG, 1L, 500ml, etc.)
   - Se ver "4KG", extraia "4KG" e mencione na descrição
   - Se ver "1L", converta para 1000ml no volume_ml

3. DESCRIÇÃO: Seja EXTREMAMENTE detalhado. Inclua:
   - Tipo completo do produto
   - Peso/volume visível
   - Características especiais (MATIC, Perfume Intenso, Nova Fórmula, etc.)
   - Uso recomendado se visível

4. VARIANTES: Extraia TODAS as variantes visíveis:
   - Peso: "4KG", "1KG", "500g"
   - Tipo: "MATIC", "Tradicional"
   - Características: "Perfume Intenso", "Nova Fórmula", "Hipoalergênico"

5. SUBCATEGORIA: Seja específico (ex: "Detergente em Pó", "Água Sanitária")

EXEMPLO DE RESPOSTA CORRETA para produto "GOTA limpa Lava Roupas em Pó 4KG":

{
  "produto": {
    "nome": "GOTA limpa Lava Roupas em Pó",
    "marca": "GOTA limpa",
    "descricao": "GOTA limpa Lava Roupas em Pó. Detergente em pó para máquinas automáticas (MATIC). Peso: 4KG. Características: Perfume Intenso, Nova Fórmula com poder de limpeza. Indicado para lavagem de roupas brancas e coloridas.",
    "categoria": "Produtos de Limpeza",
    "subcategoria": "Detergente em Pó",
    "familia_olfativa": null,
    "volume_ml": null,
    "tipo": "Lava Roupas em Pó",
    "codigo_barras": null,
    "imagens": []
  },
  "produto_generico_catalogo": {
    "nome": "GOTA limpa Lava Roupas em Pó",
    "marca": "GOTA limpa",
    "categoria": "Produtos de Limpeza",
    "subcategoria": "Detergente em Pó",
    "variantes": ["4KG", "MATIC", "Perfume Intenso", "Nova Fórmula"]
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
      "frase": "Perfume Intenso, Nova Fórmula",
      "origem": null,
      "duracao": null
    }
  }
}

⚠️ IMPORTANTE:
- Leia o nome EXATO da embalagem (não use "Produto não identificado")
- Extraia peso/volume se visível
- Preencha subcategoria (não deixe vazio)
- Extraia todas as características visíveis nas variantes
- Seja detalhado na descrição

Retorne APENAS o JSON válido, sem markdown, sem explicações."""
    
    # Criar ou atualizar prompt
    prompt, created = PromptTemplate.objects.get_or_create(
        nome="Análise de Produto - Com Exemplo v5",
        tipo_prompt="analise_imagem_produto",
        defaults={
            'prompt_text': prompt_text,
            'ativo': True,
            'eh_padrao': True,
            'versao': '5.0.0',
            'descricao': 'Prompt v5 com exemplo concreto do produto GOTA limpa. Instruções diretas com exemplo de resposta esperada.',
            'parametros': {
                'temperature': 0.1,
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
        prompt.versao = '5.0.0'
        prompt.descricao = 'Prompt v5 com exemplo concreto do produto GOTA limpa. Instruções diretas com exemplo de resposta esperada.'
        prompt.parametros = {
            'temperature': 0.1,
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
    print(f"   Temperature: 0.1")
    
    print("\n" + "="*80)
    print("✅ Prompt v5 criado!")
    print("="*80)
    print("\n📝 Melhorias principais:")
    print("   ✓ Exemplo concreto de resposta esperada")
    print("   ✓ Instruções muito diretas")
    print("   ✓ Mostra exatamente como deve ser a resposta")
    print("="*80)

if __name__ == '__main__':
    criar_prompt_v5()


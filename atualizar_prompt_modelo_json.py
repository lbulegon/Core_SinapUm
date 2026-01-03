#!/usr/bin/env python
"""
Script para atualizar o prompt de análise de imagens para retornar JSON no formato modelo.json completo
"""
import os
import sys
import django
import json

sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'setup.settings')
django.setup()

from app_sinapum.models import PromptTemplate, Sistema

def atualizar_prompt_modelo_json():
    """Atualiza o prompt para retornar JSON no formato modelo.json completo"""
    
    print("="*80)
    print("ATUALIZANDO PROMPT: Análise de Produto por Imagem - Formato modelo.json Completo")
    print("="*80)
    
    # Ler o modelo.json de referência
    modelo_json_path = "/app/docs/modelo.json"
    try:
        with open(modelo_json_path, 'r', encoding='utf-8') as f:
            modelo_json = json.load(f)
        print(f"✅ Modelo.json carregado de: {modelo_json_path}")
    except Exception as e:
        print(f"⚠️ Erro ao carregar modelo.json: {e}")
        print("   Usando estrutura de referência embutida")
        modelo_json = {
            "produto": {},
            "produto_generico_catalogo": {},
            "produto_viagem": {},
            "estabelecimento": {},
            "campanha": {},
            "shopper": {},
            "cadastro_meta": {}
        }
    
    # Criar prompt completo que solicita o formato modelo.json
    prompt_text = f"""Você é um especialista em análise de produtos. Analise esta imagem detalhadamente e retorne um JSON estruturado no formato modelo.json COMPLETO.

IMPORTANTE: Você DEVE retornar um JSON com TODAS as seções do modelo.json, mesmo que alguns campos sejam null.

Estrutura OBRIGATÓRIA do JSON de retorno:

{{
  "produto": {{
    "nome": "nome completo e exato do produto",
    "marca": "marca do produto",
    "descricao": "descrição detalhada e completa extraída da imagem",
    "categoria": "categoria principal (ex: Perfumaria, Eletrônicos, Alimentos, etc.)",
    "subcategoria": "subcategoria específica (ex: Perfume Masculino, Notebook, etc.)",
    "familia_olfativa": "família olfativa se for perfume (ex: Amadeirada, Floral, etc.) ou null",
    "volume_ml": número em ml se visível (ex: 50, 100) ou null,
    "tipo": "tipo do produto se visível (ex: Parfum, Eau de Parfum, etc.) ou null",
    "codigo_barras": "código de barras completo se visível na imagem ou null",
    "imagens": ["lista de nomes de arquivos de imagens - deixe vazio, será preenchido depois"]
  }},
  
  "produto_generico_catalogo": {{
    "nome": "nome genérico do produto (sem especificações como volume, tipo, etc.)",
    "marca": "marca do produto",
    "categoria": "categoria principal",
    "subcategoria": "subcategoria",
    "variantes": ["lista de variantes extraídas (ex: ['50ml', 'Parfum'])"]
  }},
  
  "produto_viagem": {{
    "preco_compra_usd": preço de compra em USD se visível ou null,
    "preco_compra_brl": preço de compra em BRL se visível ou null,
    "margem_lucro_percentual": margem de lucro se visível ou null,
    "preco_venda_usd": preço de venda em USD se visível ou null,
    "preco_venda_brl": preço de venda em BRL se visível na imagem ou null
  }},
  
  "estabelecimento": {{
    "nome": null,
    "endereco": null,
    "localizacao_geografica": {{
      "latitude": null,
      "longitude": null
    }},
    "observacao": null
  }},
  
  "campanha": {{
    "id": null,
    "nome": null,
    "data_registro": null
  }},
  
  "shopper": {{
    "id": null,
    "nome": null,
    "pais": null
  }},
  
  "cadastro_meta": {{
    "capturado_por": "VitrineZap (IA Évora)",
    "data_captura": "data atual no formato ISO8601 (ex: 2025-01-15T10:30:00Z)",
    "fonte": "Análise automática de imagem",
    "confianca_da_leitura": número entre 0.0 e 1.0 baseado na clareza da imagem,
    "detalhes_rotulo": {{
      "frase": "frases especiais visíveis no rótulo (ex: 'conscious & vegan formula') ou null",
      "origem": "país de origem se visível (ex: 'Made in France') ou null",
      "duracao": "informações de duração se visível (ex: 'very long-lasting') ou null"
    }}
  }}
}}

INSTRUÇÕES DETALHADAS:

1. PRODUTO:
   - Extraia TODAS as informações visíveis na imagem
   - Nome: use o nome exato e completo visível na embalagem
   - Marca: identifique a marca claramente
   - Descrição: seja detalhado, inclua ingredientes, características, especificações técnicas se visíveis
   - Categoria: use categorias comerciais padrão (Perfumaria, Eletrônicos, Alimentos, Roupas, etc.)
   - Subcategoria: seja específico (Perfume Masculino, Notebook, etc.)
   - Volume_ml: extraia se houver indicação de volume (ex: 50ml, 100ml)
   - Tipo: para perfumes, identifique tipo (Parfum, Eau de Parfum, Eau de Toilette, etc.)
   - Código de barras: extraia o código completo se visível
   - Imagens: deixe como array vazio []

2. PRODUTO_GENERICO_CATALOGO:
   - Nome: remova especificações como volume, tipo, peso (ex: "1 Million Royal" ao invés de "1 Million Royal 50ml")
   - Variantes: extraia variantes visíveis (ex: ["50ml", "Parfum"])

3. PRODUTO_VIAGEM:
   - Extraia preços se visíveis na imagem
   - Se houver apenas um preço, use como preco_venda_brl
   - Deixe outros campos como null se não visíveis

4. ESTABELECIMENTO, CAMPANHA, SHOPPER:
   - Deixe todos os campos como null (serão preenchidos depois)

5. CADASTRO_META:
   - capturado_por: sempre "VitrineZap (IA Évora)"
   - data_captura: data/hora atual no formato ISO8601
   - fonte: "Análise automática de imagem"
   - confianca_da_leitura: avalie a clareza da imagem (0.0 a 1.0)
   - detalhes_rotulo: extraia frases especiais, origem, duração se visíveis

REGRAS IMPORTANTES:
- NÃO invente informações que não estão visíveis na imagem
- Use null para campos não visíveis (não omita campos obrigatórios)
- Seja EXTREMAMENTE detalhado na descrição do produto
- Extraia TODO o texto visível na embalagem/etiqueta
- Para códigos de barras, extraia o número completo se visível
- Para preços, extraia valor e moeda se visíveis
- Mantenha a estrutura JSON exata conforme especificado acima

Retorne APENAS o JSON, sem markdown, sem explicações, sem texto adicional."""
    
    # Buscar ou criar sistema
    sistema = None
    try:
        sistema = Sistema.objects.get(codigo='evora', ativo=True)
        print(f"✅ Sistema encontrado: {sistema.codigo}")
    except Sistema.DoesNotExist:
        print("⚠️ Sistema 'evora' não encontrado, criando prompt global (sem sistema)")
        sistemas = Sistema.objects.filter(ativo=True)
        if sistemas.exists():
            sistema = sistemas.first()
            print(f"   Usando sistema: {sistema.codigo}")
    
    # Criar ou atualizar prompt
    prompt, created = PromptTemplate.objects.get_or_create(
        nome="Análise de Produto por Imagem - modelo.json Completo",
        tipo_prompt="analise_imagem_produto",
        sistema=sistema,
        defaults={
            'prompt_text': prompt_text,
            'ativo': True,
            'eh_padrao': True,
            'versao': '2.0.0',
            'descricao': 'Prompt para análise de imagens de produtos retornando JSON completo no formato modelo.json com todas as seções obrigatórias.',
            'parametros': {
                'temperature': 0.3,
                'max_tokens': 4000
            }
        }
    )
    
    if created:
        print(f"\n✅ Prompt CRIADO: {prompt.nome}")
    else:
        # Atualizar prompt existente
        prompt.prompt_text = prompt_text
        prompt.ativo = True
        prompt.eh_padrao = True
        prompt.versao = '2.0.0'
        prompt.descricao = 'Prompt para análise de imagens de produtos retornando JSON completo no formato modelo.json com todas as seções obrigatórias.'
        prompt.save()
        print(f"\n🔄 Prompt ATUALIZADO: {prompt.nome}")
    
    print(f"   ID: {prompt.id}")
    print(f"   Tipo: {prompt.tipo_prompt}")
    print(f"   Sistema: {prompt.sistema.codigo if prompt.sistema else 'Global'}")
    print(f"   Versão: {prompt.versao}")
    print(f"   Tamanho: {len(prompt.prompt_text)} caracteres")
    print(f"   Ativo: {prompt.ativo}")
    print(f"   É Padrão: {prompt.eh_padrao}")
    
    print("\n" + "="*80)
    print("✅ Prompt atualizado com sucesso!")
    print("="*80)
    print("\n📝 O prompt agora solicita:")
    print("   ✓ Estrutura completa do modelo.json")
    print("   ✓ Todas as seções obrigatórias (produto, produto_generico_catalogo, etc.)")
    print("   ✓ Campos detalhados em cada seção")
    print("   ✓ Instruções específicas para cada campo")
    print("\n🔧 Próximos passos:")
    print("   1. Teste o prompt com uma imagem de produto")
    print("   2. Verifique se o retorno está no formato modelo.json completo")
    print("   3. Se necessário, ajuste o prompt para melhorar a qualidade")
    print("="*80)

if __name__ == '__main__':
    atualizar_prompt_modelo_json()


"""
Management command para popular o banco com o prompt padrão de análise de imagem de produto
"""
from django.core.management.base import BaseCommand
from app_sinapum.models import PromptTemplate


class Command(BaseCommand):
    help = 'Popula o banco de dados com o prompt padrão de análise de imagem de produto'

    def handle(self, *args, **options):
        prompt_text = """Você é um especialista em análise de produtos. Analise esta imagem detalhadamente e retorne um JSON estruturado com TODAS as informações visíveis sobre o produto.

IMPORTANTE: Seja EXTREMAMENTE detalhado e extraia TODAS as informações possíveis da imagem, incluindo:
- Texto visível (nomes, descrições, instruções, ingredientes, etc.)
- Informações técnicas (especificações, dimensões, peso, etc.)
- Características visuais (cores, materiais, acabamentos, etc.)
- Informações de marca e modelo
- Códigos de barras ou códigos de produto (se visíveis)
- Informações nutricionais ou de composição (se visíveis)
- Qualquer outra informação relevante

Retorne um JSON completo com a seguinte estrutura:
{
  "nome": "nome completo e exato do produto",
  "descricao": "descrição detalhada e completa do produto",
  "categoria": "categoria principal do produto",
  "subcategoria": "subcategoria (se aplicável)",
  "marca": "marca do produto",
  "modelo": "modelo ou SKU (se visível)",
  "codigo_barras": "código de barras ou EAN (se visível)",
  "preco": "preço se visível na imagem",
  "moeda": "moeda do preço (se visível)",
  "caracteristicas": ["lista", "detalhada", "de", "todas", "as", "características", "visíveis"],
  "especificacoes": {
    "dimensoes": "dimensões completas se visíveis",
    "peso": "peso se visível",
    "capacidade": "capacidade se aplicável",
    "voltagem": "voltagem se visível",
    "potencia": "potência se visível",
    "outras": "qualquer outra especificação técnica visível"
  },
  "cores": ["lista", "de", "cores", "visíveis"],
  "materiais": ["lista", "de", "materiais", "identificáveis"],
  "ingredientes": ["lista", "de", "ingredientes", "se", "visível"],
  "informacoes_nutricionais": "informações nutricionais se visíveis",
  "instrucoes": "instruções de uso se visíveis",
  "garantia": "informações de garantia se visíveis",
  "origem": "país de origem se visível",
  "texto_visivel": "todo o texto visível na embalagem/imagem",
  "observacoes": "qualquer outra observação relevante"
}

Seja MUITO detalhado e extraia TODAS as informações possíveis. Não deixe campos vazios se a informação estiver visível na imagem."""

        prompt, created = PromptTemplate.objects.get_or_create(
            nome='analise_produto_imagem_v1',
            defaults={
                'descricao': 'Prompt padrão para análise de imagens de produtos. Extrai informações estruturadas em JSON de imagens de produtos.',
                'tipo_prompt': 'analise_imagem_produto',
                'prompt_text': prompt_text,
                'versao': '1.0',
                'ativo': True,
                'eh_padrao': True,
                'parametros': {
                    'temperature': 0.3,
                    'max_tokens': 4000
                },
                'observacoes': 'Prompt migrado do código hardcoded em image_analyzer.py. Este é o prompt padrão usado pelo serviço OpenMind para análise de imagens de produtos.'
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Prompt criado com sucesso: {prompt.nome}'
                )
            )
        else:
            # Atualizar o prompt existente
            prompt.prompt_text = prompt_text
            prompt.eh_padrao = True
            prompt.ativo = True
            prompt.save()
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ Prompt já existia e foi atualizado: {prompt.nome}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nPrompt ID: {prompt.id}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Tipo: {prompt.get_tipo_prompt_display()}'
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f'Status: {"✓ Ativo e Padrão" if prompt.ativo and prompt.eh_padrao else "✗ Inativo"}'
            )
        )


"""
Simulador de cozinha — Chef Agno em dry-run + exportação de dataset (JSONL).

Uso:
  python manage.py chef_agno_simulate --list
  python manage.py chef_agno_simulate --preset calma
  python manage.py chef_agno_simulate --all-presets
  python manage.py chef_agno_simulate --all-presets --export
  python manage.py chef_agno_simulate --demo-sequence --export

Não envia comandos ao MrFoo.
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from core.cognition.chef_agno.simulator import (
    CENARIOS_PRESET,
    executar_preset,
    executar_todos_presets,
    exportar_para_dataset,
    simular_sequencia,
)


class Command(BaseCommand):
    help = "Simula decisões do Chef Agno (dry-run) e opcionalmente grava dataset de treino."

    def add_arguments(self, parser):
        parser.add_argument("--list", action="store_true", help="Lista presets disponíveis")
        parser.add_argument("--preset", type=str, default="", help="Executa um preset nomeado")
        parser.add_argument(
            "--all-presets",
            action="store_true",
            help="Executa todos os presets",
        )
        parser.add_argument(
            "--demo-sequence",
            action="store_true",
            help="Encadeia 4 pedidos com estado acumulado (toy)",
        )
        parser.add_argument(
            "--export",
            action="store_true",
            help="Anexa resultados ao JSONL (CHEF_AGNO_DATASET_PATH)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Imprime JSON completo no stdout (útil para CI)",
        )

    def handle(self, *args, **options):
        if options["list"]:
            self.stdout.write("Presets: " + ", ".join(sorted(CENARIOS_PRESET.keys())))
            return

        blocos = []
        if options["preset"]:
            nome = options["preset"].strip()
            blocos.append(executar_preset(nome))
        elif options["all_presets"]:
            blocos = executar_todos_presets()
        elif options["demo_sequence"]:
            passos = [
                {"pedido": {"itens": [{"modificadores": []}], "valor_total": 40}},
                {"pedido": {"itens": [{"modificadores": ["a"]}], "valor_total": 45}},
                {
                    "pedido": {
                        "itens": [
                            {"modificadores": ["x", "y"]},
                            {"modificadores": ["z"]},
                        ],
                        "valor_total": 90,
                    }
                },
                {"pedido": {"itens": [], "valor_total": 20}, "contexto": {"carga_operacional": 0.92}},
            ]
            estado_base = {
                "pedidos_ativos_count": 8,
                "fila_em_preparo": 3,
                "fila_confirmado": 4,
                "atraso_medio_segundos": 400,
            }
            seq = simular_sequencia(passos, estado_base, hora_fixa=20)
            blocos = seq
        else:
            self.stdout.write(self.style.WARNING("Use --list, --preset, --all-presets ou --demo-sequence"))
            return

        if options["json"]:
            self.stdout.write(json.dumps(blocos, ensure_ascii=False, indent=2, default=str))
        else:
            for b in blocos:
                dr = b["dry_run"]
                label = b.get("preset") or b.get("passo", "?")
                self.stdout.write(
                    f"[{label}] acao={dr['acao_recomendada']} score={dr['score']:.2f} "
                    f"categoria={dr['categoria']} "
                    f"gargalo={dr['previsao_gargalo']['risco_gargalo']} "
                    f"carga→{dr['previsao_gargalo']['carga_prevista_curto_prazo']}"
                )

        if options["export"]:
            n = exportar_para_dataset(blocos)
            self.stdout.write(self.style.SUCCESS(f"Dataset: +{n} linha(s) em CHEF_AGNO_DATASET_PATH"))

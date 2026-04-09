"""
Simula linha de produção (prep → grill → assembly → dispatch) com Chef Agno na entrada.

Uso:
  python manage.py kitchen_pipeline_simulate
  python manage.py kitchen_pipeline_simulate --sem-chef-agno
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from core.simulator.metrics import calcular_metricas
from core.simulator.pipeline import KitchenPipeline


class Command(BaseCommand):
    help = "Simula cozinha multi-estação com priorização Chef Agno (dry-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--sem-chef-agno",
            action="store_true",
            help="Não calcula score/prioridade no admissão (só FIFO por ordem de chegada)",
        )
        parser.add_argument("--json", action="store_true", help="Saída JSON")

    def handle(self, *args, **options):
        usar_chef = not options["sem_chef_agno"]
        estado_pico = {
            "pedidos_ativos_count": 18,
            "fila_em_preparo": 6,
            "fila_confirmado": 7,
            "atraso_medio_segundos": 420,
        }
        pipe = KitchenPipeline()
        pedidos = [
            {
                "id": "A",
                "sla": 35,
                "pedido": {"itens": [], "valor_total": 25.0},
            },
            {
                "id": "B",
                "sla": 80,
                "pedido": {
                    "itens": [
                        {"modificadores": ["x", "y"]},
                        {"modificadores": ["z"]},
                    ],
                    "valor_total": 95.0,
                },
            },
            {
                "id": "C",
                "sla": 50,
                "pedido": {"itens": [{"modificadores": ["a"]}], "valor_total": 42.0},
            },
        ]
        for i, p in enumerate(pedidos):
            pipe.admitir(
                p,
                aplicar_chef_agno=usar_chef,
                estado_operacional=estado_pico,
                tempo_entrada=i,
            )

        concluidos = pipe.executar(max_ticks=400)
        metricas = calcular_metricas(concluidos, pipeline=pipe)
        gargalo = metricas.get("gargalo") or {}

        if options["json"]:
            out = {
                "concluidos": len(concluidos),
                "metricas": metricas,
                "pedidos": [
                    {
                        "id": c.get("id"),
                        "fim_dispatch": c.get("fim_dispatch"),
                        "prioridade": c.get("prioridade"),
                        "chef_agno_score": c.get("chef_agno_score"),
                    }
                    for c in concluidos
                ],
            }
            self.stdout.write(json.dumps(out, indent=2, default=str))
            return

        self.stdout.write(f"Pedidos concluídos (expedição): {len(concluidos)}")
        self.stdout.write(f"Tempo médio de ciclo: {metricas.get('tempo_medio_ciclo')}")
        self.stdout.write(f"Taxa atraso vs SLA: {metricas.get('taxa_atraso')}")
        self.stdout.write(
            f"Gargalo: estação crítica={gargalo.get('estacao_critica')} "
            f"ratio_max={gargalo.get('ratio_max')}"
        )
        for c in concluidos:
            self.stdout.write(
                f"  — {c.get('id')}: fim_dispatch={c.get('fim_dispatch')} "
                f"prioridade={c.get('prioridade', 0):.2f} score={c.get('chef_agno_score', 0):.2f}"
            )

#!/usr/bin/env python3
"""
Exemplo de execução do Agent Core (PAOR) com adaptador orbital simulado.

Na raiz do repositório Core_SinapUm:

    export DJANGO_SETTINGS_MODULE=demo_settings
    python -m agent_core.examples.run_agent_demo

O `semantic_context` abaixo simula o que o Core_SinapUm forneceria — não é regra fixa no agent_core.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    # agent_core/examples -> dois níveis acima = raiz Core_SinapUm
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if root not in sys.path:
        sys.path.insert(0, root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo_settings")

    import django

    django.setup()

    from agent_core.policies.chef_agno import ChefAgnoPolicy
    from agent_core.services.cognitive_cycle_service import CognitiveCycleService

    # Política (persona) — separada do mecanismo
    policy = ChefAgnoPolicy(
        name="chef_agno",
        priorities=("sincronizar_estoque", "validar_pedido"),
        max_iterations=5,
        decision_style="conservative",
        success_criteria={"require_all_steps_ok": True},
        limits={"max_actions_per_iteration": 3},
        require_human_before_act=False,
    )

    # Contexto semântico vindo do Core (exemplo): operações permitidas e chaves esperadas na resposta
    semantic_context = {
        "constraints": ["nao_exceder_orcamento"],
        "allowed_operations": ["dispatch", "noop"],
        "required_result_keys": ["ok"],
        "completion_signals": [],
    }

    service = CognitiveCycleService.with_simulated_orbital()

    run = service.run(
        objective="Processar fila de pedidos pendentes com validação de estoque",
        policy=policy,
        semantic_context=semantic_context,
        initial_state={"source": "demo_script"},
    )

    print("— Agent run —")
    print(f"id: {run.id}")
    print(f"status: {run.status}")
    print(f"iteracao: {run.iteracao}")
    print(f"historico (fases): {[e['phase'] for e in run.historico]}")
    print("— última auditoria —")
    if run.historico:
        print(run.historico[-1])


if __name__ == "__main__":
    main()

"""
Chef Agnos — isolamento hermético entre estabelecimentos (multi-tenant).

Regra: nenhum dado identificável ou operacional do tenant A pode influenciar a *saída*
visível ao tenant B. Aprendizado global é permitido apenas sem partilha de conteúdo
cruzado (agregação, modelos, políticas — não RAG/memória raw entre tenants).

Este ficheiro lista tarefas de implementação e verificação. Marcar conclusão em revisão
de código / testes (não persistir estado aqui).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

Scope = Literal["core", "mrfoo", "both"]


@dataclass(frozen=True, slots=True)
class TenantIsolationTask:
    """Uma tarefa verificável no código ou em testes de integração."""

    id: str
    scope: Scope
    title: str
    description: str
    verification: str


# Ordem sugerida: IDs por área (CORE / MRFOO / X-TEST)
TASKS: Final[tuple[TenantIsolationTask, ...]] = (
    TenantIsolationTask(
        id="CORE-AGNO-001",
        scope="core",
        title="tenant_id obrigatório para tráfego MrFoo",
        description=(
            "Em POST /agno/chef/message/ e fluxos decision_support ligados ao MrFoo, "
            "rejeitar ou degradar com segurança quando tenant_id estiver ausente (não assumir 'global' como contexto de resposta)."
        ),
        verification="Teste: pedido sem tenant_id → 400 ou resposta sem qualquer trecho derivado de RAG por tenant.",
    ),
    TenantIsolationTask(
        id="CORE-AGNO-002",
        scope="core",
        title="RAG e namespaces sem mistura",
        description=(
            "Garantir que core.rag_query / realidade operacional usada em decision_support "
            "filtra por tenant (prefixo id, namespace, ou metadata). Nenhum hit de documento "
            "de outro tenant no contexto do LLM ou na resposta sintetizada."
        ),
        verification="Teste com dois tenants: ingestão A; query como B não retorna ids/texto de A.",
    ),
    TenantIsolationTask(
        id="CORE-AGNO-003",
        scope="core",
        title="Cache semântico sem chaves cruzadas",
        description=(
            "Semantic cache / qualquer cache de decisão deve incluir tenant_id na chave lógica. "
            "Proibido cache hit que copie resposta de um tenant para outro."
        ),
        verification="Revisão de semantic_query/semantic_store e chaves; teste de colisão entre tenants.",
    ),
    TenantIsolationTask(
        id="CORE-AGNO-004",
        scope="core",
        title="Logs e AgnoDecisionLog sem PII cruzado",
        description=(
            "ChefAgnoDecisionLogger e logs estruturados: não gravar payloads completos de outro tenant; "
            "truncar e segregar por tenant_id onde aplicável."
        ),
        verification="Inspecionar modelo AgnoDecisionLog e payloads; grep por vazamento de IDs de pedido de outro tenant.",
    ),
    TenantIsolationTask(
        id="CORE-AGNO-005",
        scope="core",
        title="Aprendizado global sem dados brutos",
        description=(
            "Loops de feedback / learning: agregar ou anonimizar antes de modelo global; "
            "proibir escrita de texto operacional identificável de tenant A em store partilhado "
            "lido como contexto por tenant B."
        ),
        verification="Revisão order_feedback_service e pipelines de embedding; teste de não propagação de texto raw.",
    ),
    TenantIsolationTask(
        id="MRFOO-AGNO-001",
        scope="mrfoo",
        title="Cliente Core sempre com tenant explícito",
        description=(
            "chef_agno_process_message / ChefAgnoService: sempre enviar tenant_id da empresa do utilizador; "
            "nunca omitir por conveniência. Utilizador sem empresa → não usar modo core com dados sensíveis "
            "ou exigir escopo limitado."
        ),
        verification="Revisão de payload em chef_agno_service.py; teste com user sem perfil/empresa.",
    ),
    TenantIsolationTask(
        id="MRFOO-AGNO-002",
        scope="mrfoo",
        title="Resposta local (fallback) não vaza outros tenants",
        description=(
            "Orquestrador local em chef_agno/chef.py e RAG MrFoo: buscas e sessões escopadas a empresa/tenant; "
            "não reutilizar sessão ou vector de outro tenant."
        ),
        verification="Teste de sessão e RAG por empresa_id; fuzz em queries cross-tenant.",
    ),
    TenantIsolationTask(
        id="X-TEST-001",
        scope="both",
        title="Teste de fuga tenant A → B",
        description=(
            "Suite de integração: dois tenants, dados distintos no Core/RAG; "
            "perguntas ao Chef como B nunca citam marcas/nomes/pedidos de A."
        ),
        verification="CI ou script manual documentado; falha se qualquer string secreta de A aparecer na resposta B.",
    ),
)


def iter_tasks(scope: Scope | None = None) -> tuple[TenantIsolationTask, ...]:
    """Filtra tarefas por scope (core, mrfoo, both). None = todas."""
    if scope is None:
        return TASKS
    return tuple(t for t in TASKS if t.scope == scope or t.scope == "both")


__all__ = ["TenantIsolationTask", "TASKS", "iter_tasks"]

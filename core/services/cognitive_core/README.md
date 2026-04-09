# cognitive_core — núcleo cognitivo unificado

## Mapeamento Peirce (implementação)

| Conceito     | Tipo no código        | Responsabilidade |
|-------------|------------------------|------------------|
| Signo       | `PerceptionInput`      | Entrada normalizada + raw + trace |
| Objeto      | `RealityState`         | Operacional + RAG + graph (stub/extensível) |
| Interpretante | `DecisionOutput`     | Ação, confiança, raciocínio; LLM só se `use_llm_interpretant` |

## Fluxo (WhatsApp inbound)

1. `run_event_flow` → se `COGNITIVE_CORE_USE_ORCHESTRATOR=true`, chama `CognitiveOrchestrator.run_inbound_whatsapp_flow`.
2. `perception_from_inbound_event` → `CognitiveContext.from_perception` → `RealityStateBuilder.build` (RAG com namespaces).
3. `DecisionEngine.decide_inbound_whatsapp`: policy Evora → cache semântico → **EOC enrich** (`eoc_enrich_bundle`, com `precomputed_rag`) → LLM ou template.
4. Envio WhatsApp + `DecisionLog` via `UnifiedCognitiveMemory` + `domain_append_message`.

## Ferramentas MCP

| Tool | Função |
|------|--------|
| `core.eoc_enrich` | Enrich apenas (sem `ok` no núcleo enrich) |
| `core.eoc_decide` | Legado: enrich + `ok: true` |
| `core.decision_support` | Orbital (MrFoo): `DecisionEngine.decide_orbital_support` |
| `core.rag_query` | RAG direto (inalterado em contrato) |

## Migração (passo a passo)

1. Deploy código; subir `vectorstore_service` se usar RAG.
2. `python manage.py seed_core_cognitive_tools` (cria/atualiza tools).
3. Manter `COGNITIVE_CORE_USE_ORCHESTRATOR=true` (default). Em incidente, `false` restaura `flow.py` legado.
4. MrFoo: passar a preferir `core.decision_support` ou `core.eoc_enrich` (cliente `consultar_decision_support` no repo MrFoo).
5. Fase seguinte: implementar `fetch_graph_context` com driver Neo4j ou serviço HTTP dedicado (stub hoje).

## Exemplo MrFoo

`POST /core/tools/core.decision_support/execute/` com `input`: `text`, `context_hint.tenant_id`, `rag_namespaces`: `["mrfoo","global"]`.

## Exemplo WhatsApp

Nenhuma alteração de contrato externo: o pipeline Celery continua a chamar `run_event_flow(event_id)`.

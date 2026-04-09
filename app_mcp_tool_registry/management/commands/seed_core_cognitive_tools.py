"""
Seed: tools MCP cognitivas — RAG, EOC enrich, EOC legado (eoc_decide), decision_support orbital.
"""

from django.core.management.base import BaseCommand

from app_mcp_tool_registry.models import ClientApp, Tool, ToolVersion


def _ensure_mrfoo_client() -> ClientApp:
    client, _ = ClientApp.objects.get_or_create(
        key="mrfoo",
        defaults={"name": "MrFoo", "is_active": True},
    )
    if not client.api_key:
        client.generate_api_key()
        client.save()
    return client


def _upsert_tool_version(
    tool: Tool,
    version: str,
    *,
    input_schema: dict,
    output_schema: dict,
    client: ClientApp,
) -> None:
    v, _ = ToolVersion.objects.get_or_create(
        tool=tool,
        version=version,
        defaults={
            "is_active": True,
            "runtime": "noop",
            "config": {},
            "input_schema": input_schema,
            "output_schema": output_schema,
        },
    )
    v.input_schema = input_schema
    v.output_schema = output_schema
    v.runtime = "noop"
    v.is_active = True
    v.save()
    tool.current_version = v
    tool.save()
    tool.allowed_clients.add(client)


class Command(BaseCommand):
    help = "Registra tools cognitivas incl. core.autonomy_run_cycle (Fase 3)"

    def handle(self, *args, **options):
        mrfoo = _ensure_mrfoo_client()

        # --- core.rag_query ---
        t1, _ = Tool.objects.get_or_create(
            name="core.rag_query",
            defaults={
                "description": "Busca semântica no vectorstore (RAG) — retorna id, score e texto armazenado (quando existir).",
                "is_active": True,
            },
        )
        t1.is_active = True
        t1.save()
        in1 = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texto da consulta"},
                "text": {"type": "string", "description": "Alias de query"},
                "k": {"type": "integer", "default": 5},
                "include_text": {
                    "type": "boolean",
                    "default": True,
                    "description": "Incluir texto gravado no upsert (ex.: JSON de feedback MrFoo)",
                },
                "id_prefix": {
                    "type": "string",
                    "description": "Filtrar resultados cujo id começa com este prefixo (ex.: mrfoo.order_feedback:)",
                },
            },
        }
        out1 = {
            "type": "object",
            "properties": {
                "results": {"type": "array"},
                "query": {"type": "string"},
                "k": {"type": "integer"},
                "id_prefix": {"type": ["string", "null"]},
            },
        }
        _upsert_tool_version(t1, "1.0.0", input_schema=in1, output_schema=out1, client=mrfoo)

        # --- core.rag_ingest ---
        ti, _ = Tool.objects.get_or_create(
            name="core.rag_ingest",
            defaults={
                "description": "Ingestão de texto no vectorstore (chunks JSON) — complementa core.rag_query; UI em /rag-gastronomico/.",
                "is_active": True,
            },
        )
        ti.is_active = True
        ti.save()
        ini = {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Texto longo; será partido em chunks (use chunk_words)",
                },
                "chunks": {
                    "type": "array",
                    "description": "Lista de strings ou objetos {text}; ignora `text` se preenchida",
                    "items": {"type": ["string", "object"]},
                },
                "source": {"type": "string", "default": "mcp"},
                "domain": {"type": "string", "default": "gastronomia"},
                "id_prefix": {"type": "string", "default": "sinapum.rag.gastronomia"},
                "chunk_words": {"type": "integer", "default": 400},
            },
        }
        outi = {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "chunks_ingested": {"type": "integer"},
                "chunks_total": {"type": ["integer", "null"]},
                "errors": {"type": "array"},
                "domain": {"type": "string"},
                "id_prefix": {"type": "string"},
                "source": {"type": "string"},
            },
        }
        _upsert_tool_version(ti, "1.0.0", input_schema=ini, output_schema=outi, client=mrfoo)

        # --- core.eoc_enrich (nomenclatura correta) ---
        te, _ = Tool.objects.get_or_create(
            name="core.eoc_enrich",
            defaults={
                "description": "EOC enrich apenas: RAG + riscos heurísticos + enriched_context + hints (sem decisão).",
                "is_active": True,
            },
        )
        te.is_active = True
        te.save()
        ine = {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "query": {"type": "string"},
                "context_hint": {"type": "object"},
                "context": {"type": "object"},
                "k": {"type": "integer"},
                "id_prefix": {"type": "string"},
                "rag_id_prefix": {"type": "string"},
            },
        }
        oute = {
            "type": "object",
            "properties": {
                "rag": {"type": "array"},
                "riscos": {"type": "object"},
                "enriched_context": {"type": "object"},
                "hints": {"type": "object"},
            },
        }
        _upsert_tool_version(te, "1.0.0", input_schema=ine, output_schema=oute, client=mrfoo)

        # --- core.eoc_decide (legado MCP) ---
        t2, _ = Tool.objects.get_or_create(
            name="core.eoc_decide",
            defaults={
                "description": "LEGADO: mesmo que eoc_enrich + campo ok:true. Preferir core.eoc_enrich.",
                "is_active": True,
            },
        )
        t2.description = "LEGADO: mesmo que eoc_enrich + campo ok:true. Preferir core.eoc_enrich."
        t2.is_active = True
        t2.save()
        in2 = {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "query": {"type": "string"},
                "context_hint": {"type": "object"},
                "context": {"type": "object"},
                "k": {"type": "integer"},
                "id_prefix": {"type": "string"},
                "rag_id_prefix": {"type": "string"},
            },
        }
        out2 = {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "rag": {"type": "array"},
                "riscos": {"type": "object"},
                "enriched_context": {"type": "object"},
                "hints": {"type": "object"},
            },
        }
        _upsert_tool_version(t2, "1.0.0", input_schema=in2, output_schema=out2, client=mrfoo)

        # --- core.decision_support (orbital / MrFoo) ---
        td, _ = Tool.objects.get_or_create(
            name="core.decision_support",
            defaults={
                "description": "DecisionEngine modo orbital: enrich + saída mediadora (sem policy Evora).",
                "is_active": True,
            },
        )
        td.is_active = True
        td.save()
        ind = {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "query": {"type": "string"},
                "context_hint": {"type": "object"},
                "context": {"type": "object"},
                "source": {"type": "string", "description": "ex.: mrfoo"},
                "trace_id": {"type": "string"},
                "k": {"type": "integer"},
                "rag_namespaces": {
                    "oneOf": [
                        {"type": "array", "items": {"type": "string"}},
                        {"type": "string"},
                    ],
                    "description": "Namespaces RAG (ex.: mrfoo, global) ou lista",
                },
            },
        }
        outd = {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "decision": {"type": "object"},
                "enrich_preview": {"type": "object"},
            },
        }
        _upsert_tool_version(td, "1.0.0", input_schema=ind, output_schema=outd, client=mrfoo)

        # --- core.decision_feedback (Fase 2 — aprendizado) ---
        tf, _ = Tool.objects.get_or_create(
            name="core.decision_feedback",
            defaults={
                "description": "Regista outcome operacional vs decisão prevista (DecisionFeedbackRecord + opcional vectorstore).",
                "is_active": True,
            },
        )
        tf.is_active = True
        tf.save()
        inf = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string"},
                "trace_id": {"type": "string"},
                "source": {"type": "string"},
                "decision": {"type": "object"},
                "decision_action": {"type": "string"},
                "predicted": {"type": "object"},
                "outcome": {"type": "object"},
                "upsert_vectorstore": {"type": "boolean", "default": False},
            },
            "required": ["tenant_id"],
        }
        outf = {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "record_id": {"type": ["string", "null"]},
                "predicted": {"type": "object"},
            },
        }
        _upsert_tool_version(tf, "1.0.0", input_schema=inf, output_schema=outf, client=mrfoo)

        # --- core.rag_feedback_save (memória operacional / aprendizagem RAG) ---
        trg, _ = Tool.objects.get_or_create(
            name="core.rag_feedback_save",
            defaults={
                "description": "Grava feedback pós-decisão no vectorstore (camada operacional do tenant) para ranking futuro.",
                "is_active": True,
            },
        )
        trg.is_active = True
        trg.save()
        in_rg = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string"},
                "query": {"type": "string"},
                "descricao_pedido": {"type": "string"},
                "action": {"type": "string"},
                "outcome": {"type": "string", "description": "ok | atraso | falha"},
                "resultado_real": {"type": "string"},
                "impacto_rag": {"type": "integer", "default": 0},
            },
            "required": ["tenant_id"],
        }
        out_rg = {
            "type": "object",
            "properties": {
                "ok": {"type": "boolean"},
                "stored": {"type": "boolean"},
            },
        }
        _upsert_tool_version(trg, "1.0.0", input_schema=in_rg, output_schema=out_rg, client=mrfoo)

        # --- core.autonomy_run_cycle (Fase 3) ---
        ta, _ = Tool.objects.get_or_create(
            name="core.autonomy_run_cycle",
            defaults={
                "description": "Ciclo de autonomia: padrões → insights → propostas → DecisionEngine → (opcional) ACP.",
                "is_active": True,
            },
        )
        ta.is_active = True
        ta.save()
        ina = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string"},
                "trace_id": {"type": "string"},
                "operational_snapshot": {"type": "object"},
                "dynamic_metrics": {"type": "object"},
                "strategic_context": {
                    "type": "object",
                    "description": "objetivos, kpis, weights — intenção estratégica do ciclo",
                },
            },
            "required": ["tenant_id"],
        }
        outa = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
        _upsert_tool_version(ta, "1.0.0", input_schema=ina, output_schema=outa, client=mrfoo)

        # --- core.strategic_analyze (Fase 4) ---
        ts, _ = Tool.objects.get_or_create(
            name="core.strategic_analyze",
            defaults={
                "description": "Inteligência estratégica: KPIs, propostas, integração com PatternEngine e DecisionEngine.",
                "is_active": True,
            },
        )
        ts.is_active = True
        ts.save()
        ins = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string"},
                "economic_payload": {"type": "object"},
                "operational_snapshot": {"type": "object"},
                "dynamic_metrics": {"type": "object"},
                "with_decision": {"type": "boolean"},
                "objective_profile": {
                    "type": "object",
                    "description": "objectives (lista de maximize_profit|minimize_delay|balance_load) e weights opcionais",
                },
                "strategy_top_k": {"type": "integer"},
                "trace_id": {"type": "string"},
                "k": {"type": "integer"},
                "rag_namespaces": {"type": "array"},
            },
            "required": ["tenant_id"],
        }
        outs = {"type": "object"}
        _upsert_tool_version(ts, "1.0.0", input_schema=ins, output_schema=outs, client=mrfoo)

        # --- core.strategy_feedback (Fase 4) ---
        tfb, _ = Tool.objects.get_or_create(
            name="core.strategy_feedback",
            defaults={
                "description": "Feedback estratégico: impacto previsto vs realizado.",
                "is_active": True,
            },
        )
        tfb.is_active = True
        tfb.save()
        infb = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string"},
                "strategy_key": {"type": "string"},
                "proposal_id": {"type": "string"},
                "predicted_impact": {"type": "number"},
                "realized_impact": {"type": "number"},
                "payload": {"type": "object"},
            },
            "required": ["tenant_id"],
        }
        outfb = {"type": "object", "properties": {"ok": {"type": "boolean"}}}
        _upsert_tool_version(tfb, "1.0.0", input_schema=infb, output_schema=outfb, client=mrfoo)

        # --- core.strategic_advanced (multi-loja + precificação dinâmica + expansão) ---
        tadv, _ = Tool.objects.get_or_create(
            name="core.strategic_advanced",
            defaults={
                "description": "Portefólio multi-loja, recomendação de delta de preço e prontidão para expansão.",
                "is_active": True,
            },
        )
        tadv.is_active = True
        tadv.save()
        inadv = {
            "type": "object",
            "properties": {
                "tenant_id": {"type": "string"},
                "mode": {
                    "type": "string",
                    "description": "all | multi_store | pricing | expansion",
                    "default": "all",
                },
                "stores": {
                    "type": "array",
                    "description": "Lista de lojas com tenant_id, receita, margem_media_pct, carga_estimada, atraso...",
                },
                "pricing_context": {"type": "object"},
                "expansion_context": {"type": "object"},
            },
            "required": ["tenant_id"],
        }
        outadv = {"type": "object", "properties": {"ok": {"type": "boolean"}, "bundle": {"type": "object"}}}
        _upsert_tool_version(tadv, "1.0.0", input_schema=inadv, output_schema=outadv, client=mrfoo)

        self.stdout.write(
            self.style.SUCCESS(
                "Tools cognitivas registradas (incl. core.strategic_advanced, Fase 4: core.strategic_analyze, core.strategy_feedback)."
            )
        )

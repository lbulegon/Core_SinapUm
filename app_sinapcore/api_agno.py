from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any

from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from app_sinapcore.services.agno_decision_logger import ChefAgnoDecisionLogger
from app_sinapcore.services.agno_runtime import (
    get_pedidos_queryset,
    get_produto_por_id,
    get_produtos_queryset,
    merge_request_context,
)
from core.pricing.pricing_context_builder import PricingContextBuilder
from core.services.feature_flags.rollout import is_enabled
from services.agno.batch_antecipado import BatchAntecipado
from services.agno.batch_optimizer import BatchOptimizer
from services.agno.fila_inteligente import FilaInteligente
from services.agno.menu_dinamico import MenuDinamico
from services.agno.pricing_engine import PricingEngine
from services.chef_agno.conversational import run_chef_conversational_turn

logger = logging.getLogger(__name__)


def _auth_error_or_none(request: Request) -> Response | None:
    secret = (getattr(settings, "AGNO_API_SHARED_SECRET", None) or "").strip()
    if not secret:
        if settings.DEBUG:
            return None
        return Response(
            {
                "error": "AGNO_API_SHARED_SECRET não configurado",
                "hint": "Defina AGNO_API_SHARED_SECRET no Core e envie Authorization: Bearer ...",
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    token = (
        request.headers.get("X-Agno-Key")
        or request.META.get("HTTP_X_AGNO_KEY")
        or request.headers.get("X-API-KEY")
        or request.META.get("HTTP_X_API_KEY")
        or ""
    ).strip()
    auth = request.headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        token = auth[7:].strip() or token

    if token != secret:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    return None


def _json_body(request: Request) -> dict[str, Any]:
    data = request.data
    return data if isinstance(data, dict) else {}


def _disabled_response(flag: str) -> Response:
    return Response(
        {"ok": False, "error": "module_disabled", "flag": flag},
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )


def _serialize_plano_operacional(plano: dict[str, Any]) -> dict[str, Any]:
    fila_out: list[dict[str, Any]] = []
    for row in plano.get("fila_priorizada", []) or []:
        pedido = row.get("pedido")
        fila_out.append(
            {
                "pedido_id": getattr(pedido, "id", None),
                "score": row.get("score"),
                "analise": row.get("analise"),
            }
        )
    return {
        "contexto": plano.get("contexto"),
        "total_pedidos": plano.get("total_pedidos"),
        "fila_priorizada": fila_out,
        "batches_sugeridos": plano.get("batches_sugeridos"),
    }


def _decimal_to_json(val: Decimal) -> str:
    return format(val, "f")


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def agno_fila(request: Request) -> Response:
    err = _auth_error_or_none(request)
    if err is not None:
        return err
    if not is_enabled("AGNO_API_ENABLED", default=True):
        return _disabled_response("AGNO_API_ENABLED")
    if not is_enabled("AGNO_SMART_QUEUE_ENABLED", default=False):
        return _disabled_response("AGNO_SMART_QUEUE_ENABLED")

    body = _json_body(request) if request.method == "POST" else {}
    pedidos_qs = get_pedidos_queryset()
    if pedidos_qs is None:
        return Response({"ok": False, "error": "pedidos_model_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    ctx = merge_request_context(body.get("contexto") if isinstance(body.get("contexto"), dict) else {}, pedidos_qs)
    pedidos = list(pedidos_qs[:500]) if hasattr(pedidos_qs, "__getitem__") else list(pedidos_qs)
    plano = FilaInteligente.gerar_plano_operacional(pedidos, contexto=ctx)
    return Response({"ok": True, "plano": _serialize_plano_operacional(plano)}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def agno_menu(request: Request) -> Response:
    err = _auth_error_or_none(request)
    if err is not None:
        return err
    if not is_enabled("AGNO_API_ENABLED", default=True):
        return _disabled_response("AGNO_API_ENABLED")
    if not is_enabled("AGNO_DYNAMIC_MENU_ENABLED", default=False):
        return _disabled_response("AGNO_DYNAMIC_MENU_ENABLED")

    body = _json_body(request) if request.method == "POST" else {}
    pedidos_qs = get_pedidos_queryset()
    produtos_qs = get_produtos_queryset()
    if pedidos_qs is None or produtos_qs is None:
        return Response({"ok": False, "error": "domain_models_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    ctx = merge_request_context(body.get("contexto") if isinstance(body.get("contexto"), dict) else {}, pedidos_qs)
    estado = MenuDinamico.gerar_estado_cardapio(pedidos_qs, produtos_qs, contexto=ctx)
    return Response({"ok": True, "estado_cardapio": estado, "contexto": ctx}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def agno_batch(request: Request) -> Response:
    err = _auth_error_or_none(request)
    if err is not None:
        return err
    if not is_enabled("AGNO_API_ENABLED", default=True):
        return _disabled_response("AGNO_API_ENABLED")
    if not is_enabled("AGNO_SMART_BATCH_ENABLED", default=False):
        return _disabled_response("AGNO_SMART_BATCH_ENABLED")

    body = _json_body(request) if request.method == "POST" else {}
    pedidos_qs = get_pedidos_queryset()
    produtos_qs = get_produtos_queryset()
    if pedidos_qs is None or produtos_qs is None:
        return Response({"ok": False, "error": "domain_models_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    ctx = merge_request_context(body.get("contexto") if isinstance(body.get("contexto"), dict) else {}, pedidos_qs)
    pedidos = list(pedidos_qs[:500]) if hasattr(pedidos_qs, "__getitem__") else list(pedidos_qs)

    modo = (body.get("modo") or request.query_params.get("modo") or "operacional").strip().lower()
    if modo in ("antecipado", "forecast", "previsto"):
        batches = BatchAntecipado.gerar_batches_previstos(pedidos_qs, produtos_qs, contexto=ctx)
    else:
        batches = BatchOptimizer.gerar_batches_inteligentes(pedidos, contexto=ctx)

    return Response({"ok": True, "modo": modo, "batches": batches, "contexto": ctx}, status=status.HTTP_200_OK)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def agno_pricing(request: Request) -> Response:
    err = _auth_error_or_none(request)
    if err is not None:
        return err
    if not is_enabled("AGNO_API_ENABLED", default=True):
        return _disabled_response("AGNO_API_ENABLED")
    if not is_enabled("AGNO_DYNAMIC_PRICING_ENABLED", default=False):
        return _disabled_response("AGNO_DYNAMIC_PRICING_ENABLED")

    body = _json_body(request) if request.method == "POST" else {}
    product_id = body.get("produto_id") or request.query_params.get("produto_id")
    if product_id is None:
        return Response({"ok": False, "error": "produto_id_obrigatorio"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        product_id_int = int(product_id)
    except (TypeError, ValueError):
        return Response({"ok": False, "error": "produto_id_invalido"}, status=status.HTTP_400_BAD_REQUEST)

    pedidos_qs = get_pedidos_queryset()
    if pedidos_qs is None:
        return Response({"ok": False, "error": "pedidos_model_unavailable"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    produto = get_produto_por_id(product_id_int)
    if produto is None:
        return Response({"ok": False, "error": "produto_nao_encontrado"}, status=status.HTTP_404_NOT_FOUND)

    canal = str(body.get("canal") or request.query_params.get("canal") or "app")
    empresa_raw = body.get("empresa_id") if body.get("empresa_id") is not None else request.query_params.get("empresa_id")
    empresa_id = None
    if empresa_raw is not None and str(empresa_raw).strip() != "":
        try:
            empresa_id = int(empresa_raw)
        except (TypeError, ValueError):
            empresa_id = None

    builder = PricingContextBuilder()
    try:
        pc = builder.build(product_id_int, canal=canal, empresa_id=empresa_id)
    except ValueError as exc:
        err = str(exc).lower()
        if "nao_encontrado" in err or "não encontrado" in err:
            return Response({"ok": False, "error": "produto_nao_encontrado"}, status=status.HTTP_404_NOT_FOUND)
        if "empresa" in err:
            return Response({"ok": False, "error": "empresa_inconsistente", "detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"ok": False, "error": "contexto_pricing_invalido", "detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    base_ctx = body.get("contexto") if isinstance(body.get("contexto"), dict) else {}
    merged_ctx = {
        **base_ctx,
        "pricing_builder": pc.metadata,
        "demanda_builder": pc.demanda,
        "fator_tempo_builder": pc.tempo,
        "operacional_builder": pc.operacional,
    }
    ctx = merge_request_context(merged_ctx, pedidos_qs)
    preco = PricingEngine.calcular_preco_dinamico(produto, pedidos_qs, contexto=ctx)

    motivo = (
        "Preco dinamico (custo + demanda + PPA + carga + tempo) com piso de margem; "
        "contexto agregado via PricingContextBuilder"
    )
    if getattr(settings, "PRICING_LOG_PERSIST", True):
        try:
            from app_sinapcore.models.pricing_log import PricingLog

            pb = Decimal(str(pc.preco_base))
            pf = preco
            ft = (pf / pb).quantize(Decimal("0.0001")) if pb > 0 else Decimal("1.0000")
            PricingLog.objects.create(
                empresa_id=empresa_id,
                produto_id=product_id_int,
                preco_base=pb,
                preco_final=pf,
                fator_total=ft,
                fatores={
                    "builder": pc.metadata,
                    "contexto_keys": sorted(ctx.keys()),
                    "snapshot": {
                        "demanda": pc.demanda,
                        "tempo": pc.tempo,
                        "operacional": pc.operacional,
                        "canal": canal,
                    },
                },
                canal=canal,
                motivo=motivo,
            )
        except Exception:
            logger.exception("PricingLog persist falhou")

    ChefAgnoDecisionLogger.log_decision(
        module="chef_agno",
        action="SUGERIR_PRECO",
        reason=motivo,
        product_id=int(getattr(produto, "id", 0) or 0) or None,
        product_name=str(getattr(produto, "nome", "") or ""),
        payload={"preco_sugerido": _decimal_to_json(preco), "contexto": ctx},
    )

    return Response(
        {
            "ok": True,
            "produto_id": int(getattr(produto, "id", 0) or 0),
            "preco_sugerido": _decimal_to_json(preco),
            "contexto": ctx,
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def agno_chef_message(request: Request) -> Response:
    """
    Turno conversacional Chef Agnos — implementação canónica no Core (decision_support orbital).

    Body JSON (exemplo):
      {"text": "...", "user_id": "1", "channel": "web", "session_id": null,
       "tenant_id": "42", "rag_namespaces": ["mrfoo", "global"]}
    """
    err = _auth_error_or_none(request)
    if err is not None:
        return err
    if not is_enabled("AGNO_API_ENABLED", default=True):
        return _disabled_response("AGNO_API_ENABLED")
    if not is_enabled("AGNO_CHEF_MESSAGE_ENABLED", default=True):
        return _disabled_response("AGNO_CHEF_MESSAGE_ENABLED")

    body = _json_body(request)
    text = str(body.get("text") or "").strip()
    if not text:
        return Response({"ok": False, "error": "text_obrigatorio"}, status=status.HTTP_400_BAD_REQUEST)

    payload: dict[str, Any] = {
        "text": text,
        "user_id": body.get("user_id"),
        "channel": body.get("channel") or "web",
        "session_id": body.get("session_id"),
        "tenant_id": body.get("tenant_id"),
        "rag_query": body.get("rag_query"),
        "rag_namespaces": body.get("rag_namespaces"),
        "operational_snapshot": body.get("operational_snapshot"),
        "trace_id": body.get("trace_id"),
    }
    if body.get("k") is not None:
        payload["k"] = body.get("k")

    result = run_chef_conversational_turn(payload)
    try:
        ChefAgnoDecisionLogger.log_decision(
            module="chef_agno",
            action=str(result.get("intent") or "CHEF_MESSAGE")[:80],
            reason=str(result.get("response") or "")[:255],
            payload={
                "source": result.get("source"),
                "confidence": result.get("confidence"),
                "tenant_id": body.get("tenant_id"),
            },
        )
    except Exception:
        pass

    return Response({"ok": True, **result}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def agno_flags(request: Request) -> Response:
    err = _auth_error_or_none(request)
    if err is not None:
        return err

    flags = {
        "AGNO_API_ENABLED": is_enabled("AGNO_API_ENABLED", default=True),
        "AGNO_CHEF_MESSAGE_ENABLED": is_enabled("AGNO_CHEF_MESSAGE_ENABLED", default=True),
        "AGNO_SMART_QUEUE_ENABLED": is_enabled("AGNO_SMART_QUEUE_ENABLED", default=False),
        "AGNO_DYNAMIC_MENU_ENABLED": is_enabled("AGNO_DYNAMIC_MENU_ENABLED", default=False),
        "AGNO_SMART_BATCH_ENABLED": is_enabled("AGNO_SMART_BATCH_ENABLED", default=False),
        "AGNO_DYNAMIC_PRICING_ENABLED": is_enabled("AGNO_DYNAMIC_PRICING_ENABLED", default=False),
        "AGNO_CACHE_ENABLED": is_enabled("AGNO_CACHE_ENABLED", default=True),
    }
    return Response({"ok": True, "flags": flags}, status=status.HTTP_200_OK)

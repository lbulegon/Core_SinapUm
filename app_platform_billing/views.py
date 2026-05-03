"""API pública de catálogo e checkout multi-produto."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from app_platform_billing.catalog_limits import SINAPLINT_PRODUCT_SLUG
from app_platform_billing.checkout_service import create_checkout_session_url, stripe_available
from app_platform_billing.models import CatalogPlan, SaaSProduct


class PlansListView(APIView):
    """GET ?product=slug — planos públicos do catálogo plataforma."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        slug = request.query_params.get("product")
        if not slug:
            return Response(
                {"error": "Query obrigatória: product=<slug>"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        qs = CatalogPlan.objects.filter(
            product__slug=slug,
            product__is_active=True,
            is_public=True,
        ).select_related("product")
        if not qs.exists():
            return Response([], status=status.HTTP_200_OK)
        out = []
        for p in qs.order_by("sort_order", "id"):
            lim = p.limits or {}
            out.append(
                {
                    "id": p.id,
                    "product": p.product.slug,
                    "name": p.name,
                    "slug": p.slug,
                    "stripe_price_id": p.stripe_price_id,
                    "limits": lim,
                    "max_analyses_per_month": lim.get("max_analyses_per_month"),
                    "max_repos": lim.get("max_repos"),
                    "sort_order": p.sort_order,
                }
            )
        return Response(out)


class CreateCheckoutSessionView(APIView):
    """
    POST JSON: ``product`` (slug), ``plan_slug`` | ``price_id`` (Stripe).
    Metadados Stripe incluem ``product_slug`` para o webhook.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        if not stripe_available():
            return Response(
                {"error": "Stripe não configurado (STRIPE_SECRET_KEY ou pacote stripe)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        product_slug = request.data.get("product")
        if not product_slug:
            return Response({"error": "product (slug) obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

        url, err = create_checkout_session_url(
            request.user,
            str(product_slug),
            price_id=request.data.get("price_id"),
            plan_slug=request.data.get("plan_slug"),
        )
        if err:
            return Response({"error": err}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"url": url}, status=status.HTTP_200_OK)


class SinapLintCompatPlansView(APIView):
    """GET sem query — mesmo formato que o antigo ``/api/sinaplint/saas/billing/plans/``."""

    permission_classes = [AllowAny]

    def get(self, request: Request) -> Response:
        qs = CatalogPlan.objects.filter(
            product__slug=SINAPLINT_PRODUCT_SLUG,
            product__is_active=True,
            is_public=True,
        ).order_by("sort_order", "id")
        rows = []
        for p in qs:
            lim = p.limits or {}
            rows.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "stripe_price_id": p.stripe_price_id,
                    "max_analyses_per_month": lim.get("max_analyses_per_month", 0),
                    "max_repos": lim.get("max_repos", 0),
                    "sort_order": p.sort_order,
                }
            )
        return Response(rows)


class SinapLintCompatCheckoutView(APIView):
    """POST — mesmo contrato que o antigo checkout SinapLint (``plan_slug`` / ``price_id``)."""

    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        if not stripe_available():
            return Response(
                {"error": "Stripe não configurado (STRIPE_SECRET_KEY ou pacote stripe)."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        url, err = create_checkout_session_url(
            request.user,
            SINAPLINT_PRODUCT_SLUG,
            price_id=request.data.get("price_id"),
            plan_slug=request.data.get("plan_slug"),
        )
        if err:
            code = (
                status.HTTP_503_SERVICE_UNAVAILABLE
                if "Stripe não configurado" in err
                else status.HTTP_400_BAD_REQUEST
            )
            return Response({"error": err}, status=code)
        return Response({"url": url}, status=status.HTTP_200_OK)

"""
Autenticação opcional via header ``X-API-Key`` (modelo :class:`~app_sinaplint.models_api.APIKey`).

Colocar **depois** de ``AuthenticationMiddleware`` para substituir o utilizador quando a key for válida.
"""

from __future__ import annotations

from typing import Callable

from django.http import HttpRequest, HttpResponse


class SinapLintAPIKeyMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        key = request.headers.get("X-API-Key") or request.META.get("HTTP_X_API_KEY")
        if key:
            try:
                from django.utils import timezone

                from app_sinaplint.models_api import APIKey

                ak = (
                    APIKey.objects.select_related("user")
                    .filter(key=key, is_active=True)
                    .first()
                )
                if ak and ak.user.is_active:
                    request.user = ak.user
                    APIKey.objects.filter(pk=ak.pk).update(last_used_at=timezone.now())
            except Exception:
                pass
        return self.get_response(request)

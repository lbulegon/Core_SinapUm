"""Filtros de template — estado ambiental (indícios 0–1 → % de largura)."""

from __future__ import annotations

from django import template

register = template.Library()


@register.filter
def percent(value) -> str:
    """Converte valor 0–1 em percentagem 0–100 para barras CSS (sempre com ponto decimal)."""
    try:
        x = round(max(0.0, min(100.0, float(value) * 100.0)), 1)
        return f"{x:.1f}"
    except (TypeError, ValueError):
        return "0.0"

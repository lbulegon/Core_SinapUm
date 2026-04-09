import json

from django import template

register = template.Library()


@register.filter
def pretty_json(value) -> str:
    """Formata dict/list para uso dentro de <pre> (conteúdo escapado pelo motor de templates)."""
    if value is None:
        return ""
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return str(value)

"""
Creative Engine - Geração de documentos (PDF, ebook)
Integra Pandoc + LaTeX e opcionalmente OpenMind para enriquecimento de texto.
"""
from .markdown_enricher import enrich_markdown_with_ai, DEFAULT_INSTRUCTIONS

__all__ = ["enrich_markdown_with_ai", "DEFAULT_INSTRUCTIONS"]

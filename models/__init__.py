"""
Modelos de governança SinapCore (fila, auditoria, módulos).

A implementação Django vive em `app_sinapcore.models`; este pacote reexporta para
descoberta e imports consistentes com a documentação do framework.
"""

from app_sinapcore.models import (
    ArchitectureScore,
    SinapCoreCommand,
    SinapCoreLog,
    SinapCoreModule,
    SinapLintAnalysis,
    SinapLintProject,
    SinapLintTenant,
)

__all__ = [
    "SinapCoreModule",
    "SinapCoreLog",
    "SinapCoreCommand",
    "ArchitectureScore",
    "SinapLintTenant",
    "SinapLintProject",
    "SinapLintAnalysis",
]

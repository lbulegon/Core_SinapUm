from __future__ import annotations

from typing import Any

from .ppa_engine import PPAEngine


class PPAPreditivo:
    @staticmethod
    def calcular_ppa_futuro(produto: Any, demanda_prevista: float, contexto: dict | None = None) -> float:
        """
        Ajusta PPA atual com fator de demanda prevista.
        """
        ppa_base = float(PPAEngine.calcular_ppa(produto, contexto or {}))
        fator_demanda = float(demanda_prevista or 0) * 0.5
        return ppa_base + fator_demanda

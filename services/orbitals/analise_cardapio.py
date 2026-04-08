from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any


def _read_float_setting(name: str, default: float) -> float:
    """
    Lê configuração via Django settings (se disponível) ou variável de ambiente.
    Não falha se Django não estiver inicializado.
    """
    try:
        from django.conf import settings  # type: ignore

        if hasattr(settings, name):
            value = getattr(settings, name)
            return float(value)
    except Exception:
        pass

    raw = os.environ.get(name)
    if raw is None or raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass(frozen=True)
class CardapioScoreConfig:
    peso_margem: float = 0.5
    peso_volume: float = 0.4
    peso_complexidade: float = 0.3
    limite_cmv_alto: float = 0.35
    limite_volume_baixo: int = 10
    limite_complexidade_alta: float = 5.0
    max_margem_referencia: float = 100.0
    max_vendas_referencia: float = 200.0
    max_complexidade_referencia: float = 10.0

    @classmethod
    def from_runtime(cls) -> "CardapioScoreConfig":
        return cls(
            peso_margem=_read_float_setting("CARDAPIO_PESO_MARGEM", 0.5),
            peso_volume=_read_float_setting("CARDAPIO_PESO_VOLUME", 0.4),
            peso_complexidade=_read_float_setting("CARDAPIO_PESO_COMPLEXIDADE", 0.3),
            limite_cmv_alto=_read_float_setting("CARDAPIO_LIMITE_CMV_ALTO", 0.35),
            limite_volume_baixo=int(_read_float_setting("CARDAPIO_LIMITE_VOLUME_BAIXO", 10.0)),
            limite_complexidade_alta=_read_float_setting("CARDAPIO_LIMITE_COMPLEXIDADE_ALTA", 5.0),
            max_margem_referencia=_read_float_setting("CARDAPIO_MAX_MARGEM_REFERENCIA", 100.0),
            max_vendas_referencia=_read_float_setting("CARDAPIO_MAX_VENDAS_REFERENCIA", 200.0),
            max_complexidade_referencia=_read_float_setting("CARDAPIO_MAX_COMPLEXIDADE_REFERENCIA", 10.0),
        )


class CardapioAnalysisOrbital:
    """
    Orbital cognitivo de análise de cardápio.
    Independente de models/views de domínio (MrFoo).
    """

    def __init__(self, config: CardapioScoreConfig | None = None) -> None:
        self.config = config or CardapioScoreConfig.from_runtime()

    def analisar_produto(self, data: dict[str, Any]) -> dict[str, Any]:
        payload = self._sanitize_input(data)
        complexidade = self.calcular_complexidade(payload)
        score = self.calcular_score(payload, complexidade)
        classificacao = self.classificar_produto(score, payload)
        acao = self.sugerir_acao(classificacao, payload, complexidade)
        insights = self.gerar_insights(payload, complexidade)

        return {
            "produto": payload["produto"],
            "score": round(score, 2),
            "classificacao": classificacao,
            "acao": acao,
            "complexidade": round(complexidade, 2),
            "insights": insights,
            "metricas": {
                "cmv": payload["cmv"],
                "preco": payload["preco"],
                "vendas": payload["vendas"],
                "receita": payload["receita"],
                "cmv_percentual": payload["cmv_percentual"],
                "tempo_preparo": payload["tempo_preparo"],
                "etapas": payload["etapas"],
                "ingredientes": payload["ingredientes"],
            },
        }

    def calcular_complexidade(self, data: dict[str, Any]) -> float:
        tempo_preparo = float(data.get("tempo_preparo", 1.0))
        etapas = float(data.get("etapas", 1.0))
        ingredientes = float(data.get("ingredientes", 1.0))
        raw = (tempo_preparo * 0.5) + (etapas * 0.3) + (ingredientes * 0.2)
        return _clamp(raw, 0.0, self.config.max_complexidade_referencia)

    def calcular_score(self, data: dict[str, Any], complexidade: float) -> float:
        margem = float(data["preco"]) - float(data["cmv"])
        volume = float(data["vendas"])

        margem_norm = _clamp(margem / max(1.0, self.config.max_margem_referencia), 0.0, 1.0)
        volume_norm = _clamp(volume / max(1.0, self.config.max_vendas_referencia), 0.0, 1.0)
        complexidade_norm = _clamp(
            complexidade / max(1.0, self.config.max_complexidade_referencia), 0.0, 1.0
        )

        score_0_1 = (
            (margem_norm * self.config.peso_margem)
            + (volume_norm * self.config.peso_volume)
            - (complexidade_norm * self.config.peso_complexidade)
        )
        return _clamp(score_0_1 * 100.0, 0.0, 100.0)

    def classificar_produto(self, score: float, data: dict[str, Any]) -> str:
        if score >= 80:
            return "ESTRELA"
        if score >= 50:
            return "AJUSTAR"
        return "REMOVER"

    def sugerir_acao(self, classificacao: str, data: dict[str, Any], complexidade: float) -> str:
        cmv_percentual = float(data.get("cmv_percentual", 0.0))
        if classificacao == "ESTRELA":
            return "PROMOVER"
        if classificacao == "AJUSTAR":
            if cmv_percentual > self.config.limite_cmv_alto:
                return "AUMENTAR_PRECO"
            return "OTIMIZAR_PROCESSO"
        if complexidade > self.config.limite_complexidade_alta:
            return "REMOVER_ALTO_IMPACTO_OPERACIONAL"
        return "REMOVER_DO_CARDAPIO"

    def gerar_insights(self, data: dict[str, Any], complexidade: float) -> list[str]:
        insights: list[str] = []
        cmv_percentual = float(data.get("cmv_percentual", 0.0))
        vendas = int(data.get("vendas", 0))

        if cmv_percentual > self.config.limite_cmv_alto:
            insights.append("CMV elevado")
        if vendas < self.config.limite_volume_baixo:
            insights.append("Baixo volume de vendas")
        if complexidade > self.config.limite_complexidade_alta:
            insights.append("Alta complexidade operacional")
        if not insights:
            insights.append("Sem riscos críticos na análise atual")
        return insights

    def _sanitize_input(self, data: dict[str, Any]) -> dict[str, Any]:
        produto = str(data.get("produto") or "").strip() or "PRODUTO_SEM_NOME"
        cmv = max(0.0, float(data.get("cmv", 0.0) or 0.0))
        preco = max(0.0, float(data.get("preco", 0.0) or 0.0))
        vendas = max(0, int(float(data.get("vendas", 0) or 0)))
        receita = max(0.0, float(data.get("receita", 0.0) or 0.0))

        cmv_percentual_raw = data.get("cmv_percentual", None)
        if cmv_percentual_raw is None or cmv_percentual_raw == "":
            cmv_percentual = (cmv / preco) if preco > 0 else 0.0
        else:
            cmv_percentual = max(0.0, float(cmv_percentual_raw))
        cmv_percentual = _clamp(cmv_percentual, 0.0, 1.5)

        tempo_preparo = max(0.0, float(data.get("tempo_preparo", 1.0) or 0.0))
        etapas = max(0.0, float(data.get("etapas", 1.0) or 0.0))
        ingredientes = max(0.0, float(data.get("ingredientes", 1.0) or 0.0))

        return {
            "produto": produto,
            "cmv": cmv,
            "preco": preco,
            "vendas": vendas,
            "receita": receita,
            "cmv_percentual": cmv_percentual,
            "tempo_preparo": tempo_preparo,
            "etapas": etapas,
            "ingredientes": ingredientes,
        }

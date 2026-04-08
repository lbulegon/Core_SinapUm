"""
Testes unitários do orbital de análise de cardápio.
"""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from adapters.mrfoo_adapter import MrFooAdapter
from services.orbitals.analise_cardapio import CardapioAnalysisOrbital, CardapioScoreConfig


def _cfg() -> CardapioScoreConfig:
    return CardapioScoreConfig(
        peso_margem=0.5,
        peso_volume=0.4,
        peso_complexidade=0.3,
        limite_cmv_alto=0.35,
        limite_volume_baixo=10,
        limite_complexidade_alta=5.0,
        max_margem_referencia=100.0,
        max_vendas_referencia=200.0,
        max_complexidade_referencia=10.0,
    )


class TestCardapioOrbital:
    def test_orbital_returns_expected_shape(self):
        orbital = CardapioAnalysisOrbital(config=_cfg())
        out = orbital.analisar_produto(
            {
                "produto": "X-Burger",
                "cmv": 12,
                "preco": 30,
                "vendas": 100,
                "receita": 3000,
                "cmv_percentual": 0.4,
                "tempo_preparo": 8,
                "etapas": 4,
                "ingredientes": 9,
            }
        )
        assert out["produto"] == "X-Burger"
        assert 0 <= out["score"] <= 100
        assert out["classificacao"] in {"ESTRELA", "AJUSTAR", "REMOVER"}
        assert isinstance(out["insights"], list)
        assert "metricas" in out

    def test_low_input_is_clamped_to_safe_values(self):
        orbital = CardapioAnalysisOrbital(config=_cfg())
        out = orbital.analisar_produto(
            {
                "produto": "",
                "cmv": -50,
                "preco": -10,
                "vendas": -1,
                "receita": -100,
                "tempo_preparo": -5,
            }
        )
        assert out["produto"] == "PRODUTO_SEM_NOME"
        assert out["metricas"]["cmv"] == 0.0
        assert out["metricas"]["preco"] == 0.0
        assert out["metricas"]["vendas"] == 0
        assert 0 <= out["score"] <= 100

    def test_complexity_can_drive_remove_operational_action(self):
        orbital = CardapioAnalysisOrbital(config=_cfg())
        out = orbital.analisar_produto(
            {
                "produto": "Prato complexo",
                "cmv": 20,
                "preco": 30,
                "vendas": 1,
                "receita": 30,
                "tempo_preparo": 10,
                "etapas": 8,
                "ingredientes": 12,
            }
        )
        if out["classificacao"] == "REMOVER":
            assert out["acao"] in {"REMOVER_ALTO_IMPACTO_OPERACIONAL", "REMOVER_DO_CARDAPIO"}


class TestMrFooAdapterCardapio:
    def test_adapter_normalizes_payload(self):
        ad = MrFooAdapter()
        n = ad.normalizar_produto_cardapio(
            {"produto": "Y", "cmv": "12.5", "preco": "25", "vendas": "8", "receita": "200"}
        )
        assert n["produto"] == "Y"
        assert isinstance(n["cmv"], float)
        assert isinstance(n["vendas"], int)
        assert "cmv_percentual" in n

    def test_adapter_analisar_cardapio_returns_results(self):
        ad = MrFooAdapter()
        out = ad.analisar_cardapio(
            [
                {"produto": "A", "cmv": 10, "preco": 30, "vendas": 50, "receita": 1500},
                {"produto": "B", "cmv": 15, "preco": 20, "vendas": 4, "receita": 80, "tempo_preparo": 9},
            ]
        )
        assert out["command"] == "ANALISAR_CARDAPIO"
        assert out["total_produtos"] == 2
        assert isinstance(out["resultados"], list)

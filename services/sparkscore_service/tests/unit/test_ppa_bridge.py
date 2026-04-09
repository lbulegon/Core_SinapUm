"""Testes da ponte PPA ↔ orbitais."""

from app.orbitals.orbital_result import OrbitalResult
from app.orbitals.ppa_bridge import compute_pipeline_ppa, gerar_ppa_ambiental


def _mk(
    oid: str,
    status: str = "active",
    raw=None,
    score=70.0,
) -> OrbitalResult:
    return OrbitalResult(
        orbital_id=oid,
        name=oid,
        status=status,
        score=score,
        confidence=0.5,
        rationale="x",
        top_features=[],
        raw_features=raw or {},
        version="1.0.0",
    )


def test_ppa_sem_ambiental():
    results = [
        _mk("emotional", raw={"urgency_score": 0.8}),
        _mk("semiotic", raw={"goal_match": 0.7}),
        _mk("cognitive", raw={"word_count": 10, "ideal_limit": 20}),
    ]
    ppa = compute_pipeline_ppa(results, {"ppa_bridge": {"pressure_dampening_alpha": 0.12}})
    assert "antecipacao_acao" in ppa
    assert ppa["environmental_modulation"] is None
    assert ppa.get("ambiental") is None
    assert ppa["antecipacao_acao"] <= ppa["antecipacao_base"] + 1e-9


def test_gerar_ppa_ambiental():
    assert gerar_ppa_ambiental("colapso", 0.99) == 0.95
    assert gerar_ppa_ambiental("estavel", 0.1) == 0.2


def test_ppa_com_pressao_reduz_antecipacao():
    base_results = [
        _mk("emotional", raw={"urgency_score": 0.5}),
        _mk("semiotic", raw={"goal_match": 0.6}),
        _mk("cognitive", raw={"word_count": 12, "ideal_limit": 20}),
    ]
    ppa_base = compute_pipeline_ppa(base_results, {"ppa_bridge": {"pressure_dampening_alpha": 0.12}})

    with_env = base_results + [
        _mk(
            "environmental_indiciary",
            status="active",
            raw={"score_pressao": 0.95, "estado_ambiental": "sobrecarga"},
            score=88.0,
        ),
    ]
    ppa_mod = compute_pipeline_ppa(with_env, {"ppa_bridge": {"pressure_dampening_alpha": 0.12}})

    assert ppa_mod["environmental_modulation"] is not None
    assert ppa_mod["antecipacao_acao"] < ppa_base["antecipacao_acao"]
    assert ppa_mod.get("ambiental") == 0.85

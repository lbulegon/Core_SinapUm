"""
Testes de regressão para garantir que endpoints não quebram.
Compara respostas atuais com snapshots (golden files).
"""

import json
import pytest
import requests
from pathlib import Path

BASE_URL = "http://localhost:8006"
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"

# Payloads de teste (mesmos usados para gerar snapshots)
TEST_PAYLOADS = {
    "analyze": {
        "stimulus": {
            "text": "Compre agora nosso produto exclusivo com garantia total"
        },
        "context": {
            "exposure_time": 30,
            "exposure_count": 5
        }
    },
    "classify_orbital": {
        "stimulus": {
            "text": "Já vi isso antes, é familiar"
        },
        "context": {}
    },
    "semiotic": {
        "stimulus": {
            "text": "Esta é uma marca conhecida com identidade consistente"
        },
        "context": {}
    },
    "psycho": {
        "stimulus": {
            "text": "Quero muito ter isso, preciso agora"
        },
        "context": {}
    },
    "metric": {
        "stimulus": {
            "text": "Clique aqui para baixar grátis, milhares de usuários já baixaram"
        },
        "context": {
            "historical_engagement": 0.7,
            "historical_conversion": 0.5
        }
    }
}

def load_snapshot(endpoint_name: str):
    """Carrega snapshot de um endpoint"""
    snapshot_file = SNAPSHOTS_DIR / f"{endpoint_name}_snapshot.json"
    if not snapshot_file.exists():
        pytest.skip(f"Snapshot não encontrado: {snapshot_file}")
    
    with open(snapshot_file, "r", encoding="utf-8") as f:
        return json.load(f)

def normalize_response(response: dict) -> dict:
    """
    Normaliza resposta para comparação.
    Remove campos que podem variar (timestamps, etc).
    """
    normalized = json.loads(json.dumps(response))  # Deep copy
    
    # Remover campos que podem variar
    if "timestamp" in normalized:
        del normalized["timestamp"]
    
    return normalized

def compare_responses(actual: dict, expected: dict, path: str = ""):
    """
    Compara respostas recursivamente, reportando diferenças.
    """
    errors = []
    
    if isinstance(expected, dict) and isinstance(actual, dict):
        # Verificar campos obrigatórios
        for key in expected:
            if key not in actual:
                errors.append(f"Campo faltando em {path}.{key}")
            else:
                errors.extend(compare_responses(actual[key], expected[key], f"{path}.{key}"))
        
        # Avisar sobre campos extras (mas não falhar)
        for key in actual:
            if key not in expected:
                print(f"⚠️  Campo extra em {path}.{key}: {actual[key]}")
    
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            errors.append(f"Tamanho diferente em {path}: esperado {len(expected)}, obtido {len(actual)}")
        else:
            for i, (exp_item, act_item) in enumerate(zip(expected, actual)):
                errors.extend(compare_responses(act_item, exp_item, f"{path}[{i}]"))
    
    elif expected != actual:
        errors.append(f"Valor diferente em {path}: esperado {expected}, obtido {actual}")
    
    return errors

@pytest.mark.parametrize("endpoint_name,method,path,payload", [
    ("root", "GET", "/", None),
    ("health", "GET", "/health", None),
    ("sparkscore_health", "GET", "/sparkscore/health", None),
    ("orbitals", "GET", "/sparkscore/orbitals", None),
    ("analyze", "POST", "/sparkscore/analyze", TEST_PAYLOADS["analyze"]),
    ("classify_orbital", "POST", "/sparkscore/classify-orbital", TEST_PAYLOADS["classify_orbital"]),
    ("semiotic", "POST", "/sparkscore/semiotic", TEST_PAYLOADS["semiotic"]),
    ("psycho", "POST", "/sparkscore/psycho", TEST_PAYLOADS["psycho"]),
    ("metric", "POST", "/sparkscore/metric", TEST_PAYLOADS["metric"]),
])
def test_endpoint_regression(endpoint_name, method, path, payload):
    """Testa que endpoint retorna resposta compatível com snapshot"""
    snapshot = load_snapshot(endpoint_name)
    expected_response = snapshot["response"]
    
    # Fazer requisição atual
    url = f"{BASE_URL}{path}"
    if method == "GET":
        response = requests.get(url, timeout=10)
    else:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
    
    response.raise_for_status()
    actual_response = response.json()
    
    # Normalizar respostas
    expected_normalized = normalize_response(expected_response)
    actual_normalized = normalize_response(actual_response)
    
    # Comparar
    errors = compare_responses(actual_normalized, expected_normalized)
    
    if errors:
        print(f"\n❌ Diferenças encontradas em {endpoint_name}:")
        for error in errors:
            print(f"  - {error}")
        print(f"\nEsperado: {json.dumps(expected_normalized, indent=2, ensure_ascii=False)}")
        print(f"\nObtido: {json.dumps(actual_normalized, indent=2, ensure_ascii=False)}")
    
    assert len(errors) == 0, f"Resposta não compatível com snapshot para {endpoint_name}"

def test_analyze_response_structure():
    """Testa que resposta de /analyze tem estrutura esperada"""
    payload = TEST_PAYLOADS["analyze"]
    response = requests.post(
        f"{BASE_URL}/sparkscore/analyze",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    response.raise_for_status()
    data = response.json()
    
    # Verificar estrutura básica
    assert "success" in data
    assert data["success"] is True
    assert "result" in data
    
    result = data["result"]
    
    # Verificar campos obrigatórios
    assert "sparkscore" in result
    assert "ppa" in result
    assert "orbital" in result
    assert "semiotic" in result
    assert "psycho" in result
    assert "metric" in result
    assert "motor_result" in result
    assert "recommendations" in result
    
    # Verificar tipos
    assert isinstance(result["sparkscore"], (int, float))
    assert 0.0 <= result["sparkscore"] <= 1.0
    assert isinstance(result["ppa"], dict)
    assert isinstance(result["orbital"], dict)
    assert isinstance(result["recommendations"], list)


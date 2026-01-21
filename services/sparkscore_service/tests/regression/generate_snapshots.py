"""
Script para gerar snapshots de request/response dos endpoints atuais.
Execute este script quando o serviço estiver rodando para criar os golden files.
"""

import json
import requests
from pathlib import Path

BASE_URL = "http://localhost:8006"
SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"

# Criar diretório de snapshots
SNAPSHOTS_DIR.mkdir(exist_ok=True)

# Payloads de teste
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

def save_snapshot(endpoint_name: str, request_payload: dict, response: dict):
    """Salva snapshot de request/response"""
    snapshot = {
        "endpoint": endpoint_name,
        "request": request_payload,
        "response": response,
        "timestamp": None  # Será preenchido pelo script
    }
    
    snapshot_file = SNAPSHOTS_DIR / f"{endpoint_name}_snapshot.json"
    with open(snapshot_file, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Snapshot salvo: {snapshot_file}")

def test_endpoint(method: str, path: str, payload: dict = None, endpoint_name: str = None):
    """Testa endpoint e salva snapshot"""
    if endpoint_name is None:
        endpoint_name = path.replace("/", "_").replace("-", "_")
    
    url = f"{BASE_URL}{path}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
        else:
            print(f"❌ Método {method} não suportado")
            return
        
        response.raise_for_status()
        response_data = response.json()
        
        save_snapshot(endpoint_name, payload or {}, response_data)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao testar {path}: {e}")
        return None

def main():
    """Gera snapshots de todos os endpoints"""
    print("🚀 Gerando snapshots dos endpoints atuais...")
    print(f"📁 Diretório: {SNAPSHOTS_DIR}")
    print(f"🌐 Base URL: {BASE_URL}\n")
    
    # Health checks
    print("1. Testando health checks...")
    test_endpoint("GET", "/", endpoint_name="root")
    test_endpoint("GET", "/health", endpoint_name="health")
    test_endpoint("GET", "/sparkscore/health", endpoint_name="sparkscore_health")
    
    # Listar orbitais
    print("\n2. Testando listagem de orbitais...")
    test_endpoint("GET", "/sparkscore/orbitals", endpoint_name="orbitals")
    
    # Endpoints POST
    print("\n3. Testando endpoints de análise...")
    test_endpoint("POST", "/sparkscore/analyze", TEST_PAYLOADS["analyze"], "analyze")
    test_endpoint("POST", "/sparkscore/classify-orbital", TEST_PAYLOADS["classify_orbital"], "classify_orbital")
    test_endpoint("POST", "/sparkscore/semiotic", TEST_PAYLOADS["semiotic"], "semiotic")
    test_endpoint("POST", "/sparkscore/psycho", TEST_PAYLOADS["psycho"], "psycho")
    test_endpoint("POST", "/sparkscore/metric", TEST_PAYLOADS["metric"], "metric")
    
    print("\n✅ Snapshots gerados com sucesso!")
    print(f"📁 Verifique os arquivos em: {SNAPSHOTS_DIR}")

if __name__ == "__main__":
    main()


"""
Configuração dos serviços do Core_SinapUm para testes de integração.
Portas conforme docker-compose.yml.
"""

import os

# Base URL para testes (localhost quando rodando do host)
BASE_HOST = os.getenv("TEST_BASE_HOST", "localhost")

SERVICES = {
    "web": {
        "name": "Core Web (Django)",
        "port": 5000,
        "health_url": f"http://{BASE_HOST}:5000/health",
        "root_url": f"http://{BASE_HOST}:5000/",
    },
    "openmind": {
        "name": "OpenMind AI",
        "port": 8001,
        "health_url": f"http://{BASE_HOST}:8001/health",
        "root_url": f"http://{BASE_HOST}:8001/",
    },
    "mcp_service": {
        "name": "MCP Service",
        "port": 7010,
        "health_url": f"http://{BASE_HOST}:7010/health",
        "root_url": f"http://{BASE_HOST}:7010/",
    },
    "ddf_service": {
        "name": "DDF Service",
        "port": 8005,
        "health_url": f"http://{BASE_HOST}:8005/health",
        "root_url": f"http://{BASE_HOST}:8005/",
    },
    "sparkscore_service": {
        "name": "SparkScore",
        "port": 8006,
        "health_url": f"http://{BASE_HOST}:8006/health",
        "root_url": f"http://{BASE_HOST}:8006/",
        "analyze_url": f"http://{BASE_HOST}:8006/api/v1/analyze_piece",
    },
    "shopperbot_service": {
        "name": "ShopperBot",
        "port": 7030,
        "health_url": f"http://{BASE_HOST}:7030/health",
        "root_url": f"http://{BASE_HOST}:7030/",
    },
    "ifood_service": {
        "name": "iFood Service",
        "port": 7020,
        "health_url": f"http://{BASE_HOST}:7020/health",
        "root_url": f"http://{BASE_HOST}:7020/",
    },
    "chatwoot": {
        "name": "Chatwoot",
        "port": 3001,
        "health_url": f"http://{BASE_HOST}:3001/health",
        "root_url": f"http://{BASE_HOST}:3001/",
    },
    # Evolution API pode estar em stack separado
    "evolution_api": {
        "name": "Evolution API",
        "port": 8004,
        "health_url": f"http://{BASE_HOST}:8004",
        "root_url": f"http://{BASE_HOST}:8004",
    },
}

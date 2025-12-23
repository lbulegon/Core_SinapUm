#!/usr/bin/env python3
"""
Script para verificar o status de todos os serviços MCP SinapUm
"""

import subprocess
import requests
import json
from datetime import datetime

def check_container(container_name):
    """Verifica se o container está rodando"""
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None

def check_http(url, timeout=5):
    """Verifica se o endpoint HTTP está respondendo"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

print("="*70)
print("🔍 VERIFICAÇÃO DE SERVIÇOS - MCP SinapUm")
print("="*70)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

services = [
    {
        "name": "Evolution API",
        "container": "evolution_api",
        "port": 8004,
        "health_endpoint": None,  # Evolution não tem /health padrão
        "url": "http://localhost:8004"
    },
    {
        "name": "DDF",
        "container": "ddf_api",
        "port": 8005,
        "health_endpoint": "/health",
        "url": "http://localhost:8005"
    },
    {
        "name": "SparkScore",
        "container": "sparkscore_api",
        "port": 8006,
        "health_endpoint": "/health",
        "url": "http://localhost:8006"
    }
]

results = []

for service in services:
    print(f"📦 {service['name']} (Porta {service['port']})")
    print("-" * 70)
    
    # Verificar container
    status = check_container(service['container'])
    if status:
        print(f"   ✅ Container: {status}")
        container_ok = True
    else:
        print(f"   ❌ Container: Não está rodando")
        container_ok = False
    
    # Verificar HTTP
    if service['health_endpoint']:
        health_url = f"{service['url']}{service['health_endpoint']}"
        http_ok, http_status = check_http(health_url)
        if http_ok:
            print(f"   ✅ HTTP ({health_url}): OK")
        else:
            print(f"   ⚠️  HTTP ({health_url}): {http_status}")
    else:
        # Para Evolution, tentar a raiz
        http_ok, http_status = check_http(service['url'])
        if http_ok:
            print(f"   ✅ HTTP ({service['url']}): OK")
        else:
            print(f"   ⚠️  HTTP ({service['url']}): {http_status}")
    
    results.append({
        "service": service['name'],
        "container": container_ok,
        "http": http_ok
    })
    
    print()

# Verificar serviços de suporte
print("="*70)
print("🔧 SERVIÇOS DE SUPORTE")
print("="*70)
print()

support_services = [
    {"name": "PostgreSQL Evolution", "container": "postgres_evolution", "port": 5433},
    {"name": "Redis Evolution", "container": "redis_evolution", "port": 6379},
    {"name": "PostgreSQL DDF", "container": "ddf_postgres", "port": 5434},
    {"name": "Redis DDF", "container": "ddf_redis", "port": 6380},
]

for service in support_services:
    status = check_container(service['container'])
    if status:
        print(f"   ✅ {service['name']} ({service['container']}): {status}")
    else:
        print(f"   ❌ {service['name']} ({service['container']}): Não está rodando")

print()
print("="*70)
print("📊 RESUMO")
print("="*70)

all_ok = True
for result in results:
    status_icon = "✅" if (result['container'] and result['http']) else "⚠️"
    print(f"{status_icon} {result['service']}: Container={'OK' if result['container'] else 'ERRO'}, HTTP={'OK' if result['http'] else 'ERRO'}")
    if not (result['container'] and result['http']):
        all_ok = False

print()
if all_ok:
    print("🎉 Todos os serviços estão funcionando corretamente!")
else:
    print("⚠️  Alguns serviços precisam de atenção. Verifique os logs:")
    print("   docker logs <container_name>")

print()


#!/usr/bin/env python3
"""
Script para verificar se o OpenMind está unificado e funcionando corretamente
"""

import subprocess
import requests
import sys
from pathlib import Path
from datetime import datetime

def check_docker_container(container_name):
    """Verifica se container Docker está rodando"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return container_name in result.stdout
    except:
        return False

def check_port(port):
    """Verifica o que está usando uma porta"""
    try:
        result = subprocess.run(
            ["sudo", "lsof", "-i", f":{port}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
        return None
    except:
        try:
            result = subprocess.run(
                ["netstat", "-tulpn"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if f":{port}" in line and "LISTEN" in line:
                    return line.strip()
            return None
        except:
            return None

def check_http(url, timeout=5):
    """Verifica se endpoint HTTP está respondendo"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200, response.status_code, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text[:200]
    except requests.exceptions.ConnectionError:
        return False, None, "Connection refused"
    except Exception as e:
        return False, None, str(e)

def check_directory(path):
    """Verifica se diretório existe"""
    return Path(path).exists()

def check_process(pattern):
    """Verifica se processo está rodando"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return pattern in result.stdout
    except:
        return False

print("="*70)
print("🔍 VERIFICAÇÃO DO OPENMIND UNIFICADO")
print("="*70)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Verificar estrutura de pastas
print("1️⃣  ESTRUTURA DE PASTAS")
print("-"*70)

pastas_antigas = [
    ("/root/openmind_ws", "OpenMind OM1 (Docker) - DEVE SER REMOVIDA"),
    ("/opt/openmind-ai", "OpenMind AI (FastAPI) - DEVE SER REMOVIDA"),
]

pastas_novas = [
    ("/root/MCP_SinapUm/services/openmind_service", "OpenMind Unificado (FastAPI) - DEVE EXISTIR"),
]

print("\n📁 Pastas Antigas (devem ser removidas):")
for pasta, desc in pastas_antigas:
    existe = check_directory(pasta)
    status = "❌ EXISTE (deve ser removida)" if existe else "✅ Não existe (OK)"
    print(f"   {status}: {pasta}")
    print(f"      {desc}")

print("\n📁 Pasta Nova (deve existir):")
for pasta, desc in pastas_novas:
    existe = check_directory(pasta)
    status = "✅ Existe" if existe else "❌ NÃO EXISTE"
    print(f"   {status}: {pasta}")
    print(f"      {desc}")

# 2. Verificar containers Docker
print("\n2️⃣  CONTAINERS DOCKER")
print("-"*70)

containers_antigos = ["om1"]
container_novo = "openmind_service"

print("\n📦 Containers Antigos (não devem estar rodando):")
for container in containers_antigos:
    rodando = check_docker_container(container)
    status = "❌ RODANDO (deve ser parado)" if rodando else "✅ Não está rodando (OK)"
    print(f"   {status}: {container}")

print(f"\n📦 Container Novo (deve estar rodando):")
rodando_novo = check_docker_container(container_novo)
status = "✅ RODANDO" if rodando_novo else "❌ NÃO ESTÁ RODANDO"
print(f"   {status}: {container_novo}")

# 3. Verificar porta 8000
print("\n3️⃣  PORTA 8000")
print("-"*70)

port_info = check_port(8000)
if port_info:
    print(f"   ✅ Porta 8000 está em uso:")
    # Extrair informações relevantes
    lines = port_info.split('\n')
    for line in lines[:3]:  # Mostrar primeiras 3 linhas
        if line.strip():
            print(f"      {line.strip()}")
    
    # Verificar se é o container correto
    if "openmind_service" in port_info or "8000" in port_info:
        print("   ✅ Parece ser o serviço correto")
    else:
        print("   ⚠️  Verifique se é o serviço correto")
else:
    print("   ❌ Porta 8000 NÃO está em uso")

# 4. Verificar processos
print("\n4️⃣  PROCESSOS")
print("-"*70)

processos_antigos = ["uvicorn.*openmind", "openmind-ai"]
print("\n🔍 Processos Antigos (não devem estar rodando):")
for proc in processos_antigos:
    rodando = check_process(proc)
    status = "❌ RODANDO (deve ser parado)" if rodando else "✅ Não está rodando (OK)"
    print(f"   {status}: {proc}")

# 5. Verificar HTTP endpoints
print("\n5️⃣  ENDPOINTS HTTP")
print("-"*70)

endpoints = [
    ("http://localhost:8000/", "Root"),
    ("http://localhost:8000/health", "Health Check"),
    ("http://localhost:8000/docs", "Documentação Swagger"),
]

for url, nome in endpoints:
    ok, status, content = check_http(url)
    if ok:
        print(f"   ✅ {nome} ({url}): OK (Status {status})")
        if nome == "Health Check" and isinstance(content, dict):
            print(f"      Resposta: {content}")
    else:
        print(f"   ❌ {nome} ({url}): {content}")

# 6. Verificar estrutura do novo serviço
print("\n6️⃣  ESTRUTURA DO SERVIÇO UNIFICADO")
print("-"*70)

servico_path = Path("/root/MCP_SinapUm/services/openmind_service")
arquivos_importantes = [
    "docker-compose.yml",
    "Dockerfile",
    "app/main.py",
    "requirements.txt",
]

if servico_path.exists():
    print(f"   ✅ Diretório existe: {servico_path}")
    print("\n   📄 Arquivos importantes:")
    for arquivo in arquivos_importantes:
        arquivo_path = servico_path / arquivo
        existe = arquivo_path.exists()
        status = "✅" if existe else "❌"
        print(f"      {status} {arquivo}")
else:
    print(f"   ❌ Diretório não existe: {servico_path}")

# 7. Verificar logs do container
print("\n7️⃣  LOGS DO CONTAINER")
print("-"*70)

if rodando_novo:
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "10", container_novo],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("   📋 Últimas 10 linhas dos logs:")
            for line in result.stdout.strip().split('\n')[-10:]:
                if line.strip():
                    print(f"      {line.strip()}")
        else:
            print("   ⚠️  Não foi possível ler os logs")
    except:
        print("   ⚠️  Erro ao ler logs")
else:
    print("   ⚠️  Container não está rodando, não há logs")

# 8. Resumo e Status
print("\n" + "="*70)
print("📊 RESUMO E STATUS")
print("="*70)

problemas = []
aviso = []
sucessos = []

# Verificar pastas antigas
for pasta, _ in pastas_antigas:
    if check_directory(pasta):
        problemas.append(f"Pasta antiga ainda existe: {pasta}")

# Verificar container antigo
for container in containers_antigos:
    if check_docker_container(container):
        problemas.append(f"Container antigo ainda rodando: {container}")

# Verificar pasta nova
if not check_directory("/root/MCP_SinapUm/services/openmind_service"):
    problemas.append("Pasta nova não existe")

# Verificar container novo
if not rodando_novo:
    problemas.append("Container novo não está rodando")

# Verificar porta 8000
if not port_info:
    problemas.append("Porta 8000 não está em uso")

# Verificar health check
ok_health, _, _ = check_http("http://localhost:8000/health")
if not ok_health:
    aviso.append("Health check não está respondendo")

# Resultado final
print()
if problemas:
    print("❌ PROBLEMAS ENCONTRADOS:")
    for problema in problemas:
        print(f"   - {problema}")
    print()

if aviso:
    print("⚠️  AVISOS:")
    for aviso_item in aviso:
        print(f"   - {aviso_item}")
    print()

if not problemas and not aviso:
    print("✅ TUDO ESTÁ CORRETO!")
    print()
    print("   ✅ OpenMind unificado está funcionando")
    print("   ✅ Servindo na porta 8000")
    print("   ✅ Pastas antigas removidas (ou não existem)")
    print("   ✅ Container novo rodando")
    print("   ✅ Endpoints respondendo")
else:
    print("⚠️  AÇÃO NECESSÁRIA:")
    if problemas:
        print("   - Resolver os problemas listados acima")
    if aviso:
        print("   - Verificar os avisos listados acima")

print()
print("="*70)


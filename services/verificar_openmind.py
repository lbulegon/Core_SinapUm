#!/usr/bin/env python3
"""
Script para verificar qual OpenMind está rodando e onde
"""

import subprocess
import sys
from pathlib import Path

def check_process(process_name):
    """Verifica se um processo está rodando"""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return process_name in result.stdout
    except:
        return False

def check_docker_container(container_name):
    """Verifica se um container Docker está rodando"""
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
                if f":{port}" in line:
                    return line.strip()
            return None
        except:
            return None

def check_systemd_service(service_name):
    """Verifica se há serviço systemd"""
    try:
        result = subprocess.run(
            ["systemctl", "list-units", "--all", "--type=service"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return service_name in result.stdout
    except:
        return False

print("="*70)
print("🔍 VERIFICAÇÃO DE SERVIÇOS OPENMIND")
print("="*70)
print()

# 1. Verificar OpenMind AI (FastAPI) em /opt/openmind-ai
print("1️⃣  OpenMind AI Server (FastAPI) - /opt/openmind-ai/")
print("-"*70)

opt_path = Path("/opt/openmind-ai")
if opt_path.exists():
    print(f"   ✅ Diretório existe: {opt_path}")
    
    # Verificar se tem app/main.py
    main_file = opt_path / "app" / "main.py"
    if main_file.exists():
        print(f"   ✅ Aplicação encontrada: {main_file}")
    
    # Verificar processo uvicorn
    if check_process("uvicorn"):
        print("   ✅ Processo uvicorn está rodando")
    else:
        print("   ⚠️  Processo uvicorn não encontrado")
    
    # Verificar systemd
    if check_systemd_service("openmind"):
        print("   ✅ Serviço systemd encontrado")
    else:
        print("   ⚠️  Nenhum serviço systemd encontrado")
else:
    print(f"   ❌ Diretório não existe: {opt_path}")

print()

# 2. Verificar OpenMind OM1 (Docker) em /root/openmind_ws/OM1
print("2️⃣  OpenMind OM1 (Docker) - /root/openmind_ws/OM1/")
print("-"*70)

om1_path = Path("/root/openmind_ws/OM1")
if om1_path.exists():
    print(f"   ✅ Diretório existe: {om1_path}")
    
    # Verificar docker-compose.yml
    compose_file = om1_path / "docker-compose.yml"
    if compose_file.exists():
        print(f"   ✅ docker-compose.yml encontrado")
    
    # Verificar container
    if check_docker_container("om1"):
        print("   ✅ Container 'om1' está rodando")
    else:
        print("   ⚠️  Container 'om1' não está rodando")
else:
    print(f"   ❌ Diretório não existe: {om1_path}")

print()

# 3. Verificar porta 8000
print("3️⃣  Porta 8000")
print("-"*70)

port_info = check_port(8000)
if port_info:
    print(f"   ✅ Porta 8000 está em uso:")
    print(f"   {port_info}")
else:
    print("   ⚠️  Porta 8000 não está em uso")

print()

# 4. Resumo
print("="*70)
print("📊 RESUMO")
print("="*70)

services_found = []

if opt_path.exists():
    services_found.append("OpenMind AI (FastAPI) em /opt/openmind-ai/")

if om1_path.exists():
    services_found.append("OpenMind OM1 (Docker) em /root/openmind_ws/OM1/")

if services_found:
    print("\n✅ Serviços OpenMind encontrados:")
    for service in services_found:
        print(f"   - {service}")
else:
    print("\n⚠️  Nenhum serviço OpenMind encontrado nos locais esperados")

print()
print("💡 Próximos passos:")
print("   1. Decidir qual serviço migrar (ou ambos)")
print("   2. Verificar qual está realmente rodando")
print("   3. Seguir o plano em MIGRAR_OPENMIND.md")
print()


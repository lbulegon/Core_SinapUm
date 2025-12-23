#!/usr/bin/env python3
"""
Script para verificar se os serviços estão funcionando após reorganização
"""

import requests
import subprocess
import sys
from pathlib import Path

SERVICES = {
    "DDF": {
        "port": 8005,
        "health_url": "http://localhost:8005/health",
        "path": Path("/root/Core_SinapUm/services/ddf_service")
    },
    "SparkScore": {
        "port": 8006,
        "health_url": "http://localhost:8006/health",
        "path": Path("/root/Core_SinapUm/services/sparkscore_service")
    },
    "Evolution API": {
        "port": 8004,
        "health_url": "http://localhost:8004",
        "path": Path("/root/Core_SinapUm/services/evolution_api_service")
    }
}

def check_docker_containers():
    """Verifica containers Docker"""
    print("=" * 60)
    print("VERIFICANDO CONTAINERS DOCKER")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Ports}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
            
            # Verificar containers específicos
            containers = ["ddf_api", "evolution_api", "postgres_evolution", "redis_evolution"]
            for container in containers:
                check = subprocess.run(
                    ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Names}}"],
                    capture_output=True,
                    text=True
                )
                if check.stdout.strip():
                    print(f"✓ {container} está rodando")
                else:
                    print(f"✗ {container} NÃO está rodando")
        else:
            print("Erro ao verificar containers Docker")
            print(result.stderr)
    except Exception as e:
        print(f"Erro ao executar docker ps: {e}")

def check_service_paths():
    """Verifica se os caminhos dos serviços estão corretos"""
    print("\n" + "=" * 60)
    print("VERIFICANDO ESTRUTURA DE PASTAS")
    print("=" * 60)
    
    for name, config in SERVICES.items():
        path = config["path"]
        if path.exists():
            print(f"✓ {name}: {path} existe")
            
            # Verificar arquivos importantes
            if name == "DDF":
                important_files = ["docker-compose.yml", "app/main.py", "config/providers.yaml"]
            elif name == "SparkScore":
                important_files = ["docker-compose.yml", "app/core/orbital_classifier.py", "config/orbitals.yaml"]
            elif name == "Evolution API":
                important_files = ["docker-compose.yml"]
            
            for file in important_files:
                file_path = path / file
                if file_path.exists():
                    print(f"  ✓ {file} existe")
                else:
                    print(f"  ✗ {file} NÃO existe")
        else:
            print(f"✗ {name}: {path} NÃO existe")

def check_http_services():
    """Verifica serviços HTTP"""
    print("\n" + "=" * 60)
    print("VERIFICANDO SERVIÇOS HTTP")
    print("=" * 60)
    
    for name, config in SERVICES.items():
        url = config["health_url"]
        port = config["port"]
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 404]:  # 404 pode ser OK se o endpoint não existe mas o servidor responde
                print(f"✓ {name} (porta {port}): Servidor respondendo")
                if response.status_code == 200:
                    print(f"  Status: {response.status_code}")
            else:
                print(f"⚠ {name} (porta {port}): Status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"✗ {name} (porta {port}): Servidor NÃO está respondendo")
        except requests.exceptions.Timeout:
            print(f"⚠ {name} (porta {port}): Timeout ao conectar")
        except Exception as e:
            print(f"✗ {name} (porta {port}): Erro - {e}")

def check_docker_compose_files():
    """Verifica docker-compose.yml"""
    print("\n" + "=" * 60)
    print("VERIFICANDO DOCKER-COMPOSE.YML")
    print("=" * 60)
    
    for name, config in SERVICES.items():
        compose_file = config["path"] / "docker-compose.yml"
        if compose_file.exists():
            print(f"✓ {name}: docker-compose.yml existe")
            
            # Verificar se está configurado corretamente
            try:
                content = compose_file.read_text()
                if "./" in content or "pg_data" in content or "redis_data" in content:
                    print(f"  ✓ Configuração de volumes parece correta")
            except:
                pass
        else:
            print(f"✗ {name}: docker-compose.yml NÃO existe")

def main():
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO DE SERVIÇOS - MCP SinapUm")
    print("=" * 60 + "\n")
    
    check_service_paths()
    check_docker_compose_files()
    check_docker_containers()
    check_http_services()
    
    print("\n" + "=" * 60)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()


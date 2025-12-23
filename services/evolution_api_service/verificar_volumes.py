#!/usr/bin/env python3
"""
Script para verificar e limpar volumes do Docker relacionados ao Evolution API
"""

import subprocess
import json
from pathlib import Path

print("🔍 Verificando volumes do Docker...\n")

# Listar todos os volumes
result = subprocess.run(
    ["docker", "volume", "ls", "--format", "json"],
    capture_output=True,
    text=True
)

volumes = []
for line in result.stdout.strip().split('\n'):
    if line:
        try:
            volumes.append(json.loads(line))
        except:
            pass

print(f"📦 Total de volumes: {len(volumes)}\n")

# Verificar volumes relacionados ao Evolution
evolution_volumes = [v for v in volumes if 'evolution' in v.get('Name', '').lower()]

if evolution_volumes:
    print("⚠️  Volumes do Evolution encontrados:")
    for vol in evolution_volumes:
        print(f"   - {vol['Name']}")
    
    print("\n💡 Para remover volumes órfãos:")
    print("   docker volume rm <nome_do_volume>")
else:
    print("✅ Nenhum volume nomeado do Evolution encontrado")

# Verificar bind mounts (caminhos absolutos)
print("\n🔍 Verificando bind mounts nos containers...\n")

result = subprocess.run(
    ["docker", "ps", "-a", "--format", "json"],
    capture_output=True,
    text=True
)

containers = []
for line in result.stdout.strip().split('\n'):
    if line:
        try:
            containers.append(json.loads(line))
        except:
            pass

evolution_containers = [c for c in containers if 'evolution' in c.get('Names', '').lower()]

if evolution_containers:
    print("📋 Containers do Evolution:")
    for container in evolution_containers:
        print(f"\n   Container: {container['Names']}")
        # Inspectar o container para ver os mounts
        inspect_result = subprocess.run(
            ["docker", "inspect", container['Names'], "--format", "{{json .Mounts}}"],
            capture_output=True,
            text=True
        )
        if inspect_result.stdout:
            try:
                mounts = json.loads(inspect_result.stdout)
                for mount in mounts:
                    if mount.get('Type') == 'bind':
                        source = mount.get('Source', '')
                        if '/root/evolution_api' in source:
                            print(f"      ⚠️  BIND MOUNT ANTIGO: {source}")
                        else:
                            print(f"      ✅ {source}")
            except:
                pass

print("\n" + "="*60)
print("📁 Verificando pasta /root/evolution_api...")
print("="*60)

old_path = Path("/root/evolution_api")
if old_path.exists():
    print(f"\n⚠️  A pasta {old_path} ainda existe!")
    print(f"   Tamanho: {sum(f.stat().st_size for f in old_path.rglob('*') if f.is_file()) / (1024*1024):.2f} MB")
    print(f"\n   Conteúdo:")
    for item in old_path.iterdir():
        if item.is_dir():
            size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
            print(f"      📁 {item.name}/ ({size / (1024*1024):.2f} MB)")
        else:
            print(f"      📄 {item.name}")
    
    print("\n💡 Para remover completamente:")
    print("   sudo rm -rf /root/evolution_api")
else:
    print("\n✅ A pasta /root/evolution_api não existe mais!")

print("\n" + "="*60)
print("📁 Verificando pasta nova /root/MCP_SinapUm/services/evolution_api...")
print("="*60)

new_path = Path("/root/MCP_SinapUm/services/evolution_api")
if new_path.exists():
    print(f"\n✅ Pasta nova existe!")
    volumes_in_new = ['pg_data', 'redis_data', 'instances', 'storage', 'mongo_data']
    for vol in volumes_in_new:
        vol_path = new_path / vol
        if vol_path.exists():
            size = sum(f.stat().st_size for f in vol_path.rglob('*') if f.is_file())
            print(f"   ✅ {vol}/ ({size / (1024*1024):.2f} MB)")
        else:
            print(f"   ⚠️  {vol}/ não existe ainda")


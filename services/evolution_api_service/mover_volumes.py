#!/usr/bin/env python3
"""
Script para mover volumes do Evolution API de /root/evolution_api/ 
para /root/MCP_SinapUm/services/evolution_api/
"""

import shutil
import os
from pathlib import Path

SOURCE = Path("/root/evolution_api")
DEST = Path("/root/MCP_SinapUm/services/evolution_api")

volumes = ["pg_data", "redis_data", "instances", "storage", "mongo_data"]

print("Movendo volumes do Evolution API...")
print(f"Origem: {SOURCE}")
print(f"Destino: {DEST}\n")

for volume in volumes:
    source_volume = SOURCE / volume
    dest_volume = DEST / volume
    
    if source_volume.exists():
        print(f"Movendo {volume}...")
        try:
            # Criar diretório de destino se não existir
            dest_volume.mkdir(parents=True, exist_ok=True)
            
            # Copiar conteúdo
            if source_volume.is_dir():
                for item in source_volume.iterdir():
                    dest_item = dest_volume / item.name
                    if item.is_dir():
                        if dest_item.exists():
                            shutil.rmtree(dest_item)
                        shutil.copytree(item, dest_item)
                    else:
                        shutil.copy2(item, dest_item)
                print(f"  ✓ {volume} movido com sucesso")
            else:
                shutil.copy2(source_volume, dest_volume)
                print(f"  ✓ {volume} movido com sucesso")
        except Exception as e:
            print(f"  ✗ Erro ao mover {volume}: {e}")
    else:
        print(f"  - {volume} não existe, pulando...")

print("\nVolumes movidos!")
print("Agora você pode remover /root/evolution_api/")


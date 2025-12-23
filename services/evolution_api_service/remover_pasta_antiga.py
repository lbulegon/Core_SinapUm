#!/usr/bin/env python3
"""
Script para remover a pasta antiga /root/evolution_api
"""

import shutil
from pathlib import Path

OLD_PATH = Path("/root/evolution_api")

if OLD_PATH.exists():
    print(f"Removendo pasta antiga: {OLD_PATH}")
    try:
        shutil.rmtree(OLD_PATH)
        print(f"✓ Pasta {OLD_PATH} removida com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao remover: {e}")
else:
    print(f"✓ Pasta {OLD_PATH} não existe mais (já foi removida)")


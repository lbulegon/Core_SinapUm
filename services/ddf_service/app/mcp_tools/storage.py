"""
Storage Manager - Gerencia armazenamento de artefatos via MCP
"""

import os
from typing import Optional
from pathlib import Path


class StorageManager:
    """Gerencia armazenamento de artefatos (imagens, PDFs, áudios)"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or os.getenv('STORAGE_PATH', '/root/ddf/storage'))
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Criar subdiretórios
        (self.base_path / 'images').mkdir(exist_ok=True)
        (self.base_path / 'videos').mkdir(exist_ok=True)
        (self.base_path / 'audios').mkdir(exist_ok=True)
        (self.base_path / 'documents').mkdir(exist_ok=True)
    
    async def save_artifact(
        self, 
        request_id: str, 
        artifact_url: str, 
        artifact_type: str
    ) -> str:
        """
        Salva artefato (imagem, vídeo, áudio, documento)
        
        Args:
            request_id: ID da requisição
            artifact_url: URL ou caminho do artefato
            artifact_type: Tipo (image, video, audio, document)
        
        Returns:
            Caminho onde o artefato foi salvo
        """
        # Mapear tipo para diretório
        type_map = {
            'image': 'images',
            'video': 'videos',
            'audio': 'audios',
            'document': 'documents'
        }
        
        subdir = type_map.get(artifact_type, 'documents')
        target_dir = self.base_path / subdir
        target_dir.mkdir(exist_ok=True)
        
        # TODO: Implementar download real do artefato
        # Por enquanto, apenas retorna caminho simulado
        file_path = target_dir / f"{request_id}_{artifact_type}"
        
        return str(file_path)
    
    def get_artifact_path(self, request_id: str, artifact_type: str) -> Optional[str]:
        """Obtém caminho de um artefato"""
        type_map = {
            'image': 'images',
            'video': 'videos',
            'audio': 'audios',
            'document': 'documents'
        }
        
        subdir = type_map.get(artifact_type, 'documents')
        target_dir = self.base_path / subdir
        
        # Buscar arquivo com request_id
        for file in target_dir.glob(f"{request_id}*"):
            return str(file)
        
        return None


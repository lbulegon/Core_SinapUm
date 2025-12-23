"""
Queue Manager - Gerencia filas de tarefas via MCP
"""

import redis
import json
import os
from typing import Dict, Optional, Any
from datetime import datetime


class QueueManager:
    """Gerencia filas de tarefas assíncronas"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://redis:6379/0')
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        self.default_queue = 'ddf_tasks'
    
    async def enqueue_task(
        self, 
        task_type: str,
        payload: Dict,
        queue_name: Optional[str] = None,
        priority: int = 0
    ) -> str:
        """
        Adiciona tarefa à fila
        
        Args:
            task_type: Tipo da tarefa (ex: 'generate_image', 'transcribe_audio')
            payload: Dados da tarefa
            queue_name: Nome da fila (opcional)
            priority: Prioridade (0 = normal, 1 = alta, -1 = baixa)
        
        Returns:
            ID da tarefa
        """
        queue = queue_name or self.default_queue
        
        task_id = f"{task_type}_{datetime.utcnow().timestamp()}"
        
        task_data = {
            'id': task_id,
            'type': task_type,
            'payload': payload,
            'priority': priority,
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Adicionar à fila ordenada (sorted set) para suportar prioridade
        score = priority * 1000000 + datetime.utcnow().timestamp()
        self.redis_client.zadd(f"{queue}:pending", {task_id: score})
        
        # Salvar dados da tarefa
        self.redis_client.setex(
            f"{queue}:task:{task_id}",
            86400,  # 24 horas
            json.dumps(task_data)
        )
        
        return task_id
    
    async def dequeue_task(self, queue_name: Optional[str] = None) -> Optional[Dict]:
        """
        Remove e retorna próxima tarefa da fila
        
        Args:
            queue_name: Nome da fila (opcional)
        
        Returns:
            Dados da tarefa ou None se fila vazia
        """
        queue = queue_name or self.default_queue
        
        # Obter tarefa com maior prioridade
        tasks = self.redis_client.zrange(f"{queue}:pending", 0, 0, withscores=True)
        
        if not tasks:
            return None
        
        task_id, _ = tasks[0]
        
        # Remover da fila
        self.redis_client.zrem(f"{queue}:pending", task_id)
        
        # Obter dados da tarefa
        task_data_str = self.redis_client.get(f"{queue}:task:{task_id}")
        
        if not task_data_str:
            return None
        
        task_data = json.loads(task_data_str)
        task_data['status'] = 'processing'
        
        # Atualizar status
        self.redis_client.setex(
            f"{queue}:task:{task_id}",
            86400,
            json.dumps(task_data)
        )
        
        return task_data
    
    async def get_task_status(self, task_id: str, queue_name: Optional[str] = None) -> Optional[Dict]:
        """
        Obtém status de uma tarefa
        
        Args:
            task_id: ID da tarefa
            queue_name: Nome da fila (opcional)
        
        Returns:
            Dados da tarefa ou None se não encontrada
        """
        queue = queue_name or self.default_queue
        
        task_data_str = self.redis_client.get(f"{queue}:task:{task_id}")
        
        if not task_data_str:
            return None
        
        return json.loads(task_data_str)
    
    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        queue_name: Optional[str] = None
    ):
        """
        Atualiza status de uma tarefa
        
        Args:
            task_id: ID da tarefa
            status: Novo status (pending, processing, completed, failed)
            result: Resultado da tarefa (opcional)
            error: Mensagem de erro (opcional)
            queue_name: Nome da fila (opcional)
        """
        queue = queue_name or self.default_queue
        
        task_data_str = self.redis_client.get(f"{queue}:task:{task_id}")
        
        if not task_data_str:
            return
        
        task_data = json.loads(task_data_str)
        task_data['status'] = status
        task_data['updated_at'] = datetime.utcnow().isoformat()
        
        if result:
            task_data['result'] = result
        
        if error:
            task_data['error'] = error
        
        # Salvar atualização
        self.redis_client.setex(
            f"{queue}:task:{task_id}",
            86400,
            json.dumps(task_data)
        )
        
        # Se completou ou falhou, mover para fila de histórico
        if status in ['completed', 'failed']:
            self.redis_client.zadd(
                f"{queue}:history",
                {task_id: datetime.utcnow().timestamp()}
            )


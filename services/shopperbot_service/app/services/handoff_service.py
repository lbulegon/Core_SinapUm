"""Serviço de handoff para humano"""
import uuid
from datetime import datetime
from app.schemas.handoff import HandoffRequest, HandoffResponse


class HandoffService:
    """Gerencia handoff para atendimento humano"""
    
    def __init__(self):
        # Em produção, isso seria uma fila/DB
        self.queue = []
    
    def request_handoff(self, request: HandoffRequest) -> HandoffResponse:
        """Solicita handoff para humano"""
        queue_id = str(uuid.uuid4())
        
        # Criar entrada na fila (em produção seria DB/fila real)
        queue_entry = {
            "queue_id": queue_id,
            "user_id": request.user_id,
            "group_id": request.group_id,
            "estabelecimento_id": request.estabelecimento_id,
            "caso": request.caso,
            "contexto": request.contexto,
            "suggested_role": request.suggested_human_role,
            "urgency": request.urgency,
            "created_at": datetime.utcnow().isoformat(),
            "status": "queued"
        }
        
        self.queue.append(queue_entry)
        
        # Calcular tempo estimado (simplificado)
        estimated_wait = self._estimate_wait_time(request.urgency)
        
        return HandoffResponse(
            success=True,
            queue_id=queue_id,
            assigned_to=None,  # Em produção, seria atribuído aqui
            estimated_wait_time=estimated_wait,
            message=f"Sua solicitação foi registrada (ID: {queue_id[:8]}). Um atendente entrará em contato em breve."
        )
    
    def _estimate_wait_time(self, urgency: float) -> int:
        """Estima tempo de espera em segundos"""
        # Simulação: urgência alta = menos tempo
        base_time = 300  # 5 minutos base
        if urgency >= 0.8:
            return 60  # 1 minuto
        elif urgency >= 0.5:
            return 180  # 3 minutos
        return base_time


"""
Modelo de Auditoria - Registra todas as operações do DDF
"""

from datetime import datetime
from typing import Dict, Optional
import uuid


class AuditLog:
    """Modelo de log de auditoria"""
    
    def __init__(
        self,
        request_id: str,
        category: str,
        provider: str,
        input_text: str,
        detection: Dict,
        delegation: Dict,
        result: Optional[Dict] = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
        context: Optional[Dict] = None
    ):
        self.request_id = request_id
        self.category = category
        self.provider = provider
        self.input_text = input_text
        self.detection = detection
        self.delegation = delegation
        self.result = result
        self.error = error
        self.execution_time = execution_time
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.status = 'error' if error else 'success'
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'request_id': self.request_id,
            'category': self.category,
            'provider': self.provider,
            'input': self.input_text,
            'detection': self.detection,
            'delegation': self.delegation,
            'result': self.result,
            'error': self.error,
            'execution_time': self.execution_time,
            'context': self.context,
            'timestamp': self.timestamp,
            'status': self.status
        }


def create_audit_log(
    request_id: str,
    category: str,
    provider: str,
    input_text: str,
    detection: Dict,
    delegation: Dict,
    result: Optional[Dict] = None,
    error: Optional[str] = None,
    execution_time: Optional[float] = None,
    context: Optional[Dict] = None
) -> AuditLog:
    """Cria um log de auditoria"""
    return AuditLog(
        request_id=request_id,
        category=category,
        provider=provider,
        input_text=input_text,
        detection=detection,
        delegation=delegation,
        result=result,
        error=error,
        execution_time=execution_time,
        context=context
    )


def audit_log(
    request_id: str,
    category: str,
    provider: str,
    input_text: str,
    detection: Optional[Dict] = None,
    delegation: Optional[Dict] = None
) -> Dict:
    """
    Função helper para criar log de auditoria simples
    Mantida para compatibilidade
    """
    return {
        'request_id': request_id,
        'category': category,
        'provider': provider,
        'input': input_text,
        'detection': detection or {},
        'delegation': delegation or {},
        'timestamp': datetime.utcnow().isoformat()
    }


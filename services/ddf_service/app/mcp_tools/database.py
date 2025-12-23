"""
Database Manager - Gerencia persistência via MCP
"""

import os
from typing import Optional, Dict
from sqlalchemy import create_engine, Column, String, Text, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()


class AuditLogModel(Base):
    """Modelo de log de auditoria no banco"""
    __tablename__ = 'audit_logs'
    
    request_id = Column(String, primary_key=True)
    category = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    input_text = Column(Text)
    detection = Column(JSON)
    delegation = Column(JSON)
    result = Column(JSON)
    error = Column(Text)
    execution_time = Column(Float)
    context = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default='success')


class DatabaseManager:
    """Gerencia operações de banco de dados"""
    
    def __init__(self):
        database_url = os.getenv(
            'DATABASE_URL',
            'postgresql://ddf:ddf@postgres:5432/ddf'
        )
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Criar tabelas se não existirem
        Base.metadata.create_all(self.engine)
    
    async def save_audit_log(self, audit_log):
        """Salva log de auditoria no banco"""
        session = self.SessionLocal()
        try:
            log_model = AuditLogModel(
                request_id=audit_log.request_id,
                category=audit_log.category,
                provider=audit_log.provider,
                input_text=audit_log.input_text,
                detection=audit_log.detection,
                delegation=audit_log.delegation,
                result=audit_log.result,
                error=audit_log.error,
                execution_time=audit_log.execution_time,
                context=audit_log.context,
                timestamp=datetime.fromisoformat(audit_log.timestamp),
                status=audit_log.status
            )
            session.add(log_model)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    async def get_audit_log(self, request_id: str) -> Optional[Dict]:
        """Obtém log de auditoria do banco"""
        session = self.SessionLocal()
        try:
            log = session.query(AuditLogModel).filter_by(request_id=request_id).first()
            if log:
                return {
                    'request_id': log.request_id,
                    'category': log.category,
                    'provider': log.provider,
                    'input_text': log.input_text,
                    'detection': log.detection,
                    'delegation': log.delegation,
                    'result': log.result,
                    'error': log.error,
                    'execution_time': log.execution_time,
                    'context': log.context,
                    'timestamp': log.timestamp.isoformat(),
                    'status': log.status
                }
            return None
        finally:
            session.close()


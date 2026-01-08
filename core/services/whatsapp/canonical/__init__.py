"""
WhatsApp Canonical Events v1.0
==============================

Sistema de eventos canônicos para padronizar eventos de diferentes providers WhatsApp.

NOTA: Esta é uma camada ADITIVA. Não altera código existente.
"""
from .schemas import (
    EventEnvelope,
    MessagePayload,
    MediaPayload,
    StatusPayload,
    LocationPayload,
    ContactPayload,
    EventType,
    EventSource,
)
from .normalizer import EventNormalizer, get_event_normalizer
from .publisher import EventPublisher, get_event_publisher

__all__ = [
    'EventEnvelope',
    'MessagePayload',
    'MediaPayload',
    'StatusPayload',
    'LocationPayload',
    'ContactPayload',
    'EventType',
    'EventSource',
    'EventNormalizer',
    'get_event_normalizer',
    'EventPublisher',
    'get_event_publisher',
]

__version__ = '1.0.0'

"""
WhatsApp Routing - Roteamento e Atribuição SKM
==============================================

Sistema de roteamento para mensagens em grupo e atribuição de SKM.
"""
from .router import WhatsAppRouter, get_whatsapp_router
from .assignment import AssignmentPolicy, get_assignment_policy

__all__ = [
    'WhatsAppRouter',
    'get_whatsapp_router',
    'AssignmentPolicy',
    'get_assignment_policy',
]

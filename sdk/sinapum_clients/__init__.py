"""
SinapUm Clients SDK - Clientes HTTP para serviços do Core_SinapUm

Uso em orbitais (Evora, MrFoo, etc.):
    from sinapum_clients import CreativeEngineClient, SparkScoreClient, WhatsAppGatewayClient
"""
from .creative_engine import CreativeEngineClient
from .sparkscore import SparkScoreClient
from .shopperbot import ShopperBotClient
from .openmind import OpenMindClient
from .whatsapp_gateway import WhatsAppGatewayClient

__all__ = [
    "CreativeEngineClient",
    "SparkScoreClient",
    "ShopperBotClient",
    "OpenMindClient",
    "WhatsAppGatewayClient",
]

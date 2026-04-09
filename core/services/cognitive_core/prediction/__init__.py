"""Previsão operacional a partir de histórico + sinais em tempo real."""
from core.services.cognitive_core.prediction.delay_predictor import predict_delay_risk

__all__ = ["predict_delay_risk"]
